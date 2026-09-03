-- ====================================================================
-- Script DDL: Criação de Views Analíticas Consolidadas
-- Locadora de Veículos Analytics
-- ====================================================================

-- 1. View: Faturamento e Volume por Categoria de Veículo
-- Utiliza JOIN, GROUP BY, SUM, COUNT, AVG e ROUND
CREATE VIEW IF NOT EXISTS vw_faturamento_por_categoria AS
SELECT 
    c.id_categoria,
    c.nome AS categoria,
    c.valor_diaria_base,
    COUNT(l.id_locacao) AS total_locacoes,
    ROUND(COALESCE(SUM(l.valor_total), 0), 2) AS faturamento_total,
    ROUND(COALESCE(AVG(l.valor_total), 0), 2) AS ticket_medio_locacao,
    ROUND(COALESCE(AVG(l.valor_diaria), 0), 2) AS valor_diaria_media
FROM categorias c
LEFT JOIN veiculos v ON c.id_categoria = v.id_categoria
LEFT JOIN locacoes l ON v.id_veiculo = l.id_veiculo
GROUP BY c.id_categoria, c.nome, c.valor_diaria_base
ORDER BY faturamento_total DESC;

-- 2. View: Ranking e Desempenho de Clientes (Top Clientes)
-- Utiliza JOIN, GROUP BY, COUNT, SUM, AVG, MAX e ORDER BY
CREATE VIEW IF NOT EXISTS vw_desempenho_clientes AS
SELECT 
    cli.id_cliente,
    cli.nome AS cliente,
    cli.cpf,
    cli.cidade,
    cli.estado,
    COUNT(l.id_locacao) AS total_locacoes,
    ROUND(COALESCE(SUM(l.valor_total), 0), 2) AS total_gasto,
    ROUND(COALESCE(AVG(l.valor_total), 0), 2) AS ticket_medio,
    MAX(l.data_locacao) AS ultima_locacao
FROM clientes cli
LEFT JOIN locacoes l ON cli.id_cliente = l.id_cliente
GROUP BY cli.id_cliente, cli.nome, cli.cpf, cli.cidade, cli.estado
ORDER BY total_gasto DESC;

-- 3. View: Histórico Detalhado de Locações
-- Utiliza múltiplos INNER JOINs unindo 4 tabelas
CREATE VIEW IF NOT EXISTS vw_historico_locacoes_detalhado AS
SELECT 
    l.id_locacao,
    cli.nome AS cliente,
    cli.cpf AS cpf_cliente,
    cli.telefone,
    v.marca || ' ' || v.modelo AS veiculo,
    v.placa,
    cat.nome AS categoria,
    l.data_locacao,
    l.data_devolucao_prevista,
    l.data_devolucao_real,
    (JULIANDAY(l.data_devolucao_prevista) - JULIANDAY(l.data_locacao)) AS dias_previstos,
    l.valor_diaria,
    l.valor_total,
    l.status AS status_locacao
FROM locacoes l
INNER JOIN clientes cli ON l.id_cliente = cli.id_cliente
INNER JOIN veiculos v ON l.id_veiculo = v.id_veiculo
INNER JOIN categorias cat ON v.id_categoria = cat.id_categoria
ORDER BY l.data_locacao DESC;

-- 4. View: Resultado Operacional por Veículo (Receita vs Custos de Manutenção)
-- Utiliza Subqueries, LEFT JOINs e Funções de Agregação
CREATE VIEW IF NOT EXISTS vw_resultado_por_veiculo AS
SELECT 
    v.id_veiculo,
    v.marca || ' ' || v.modelo AS veiculo,
    v.placa,
    v.status AS status_atual,
    v.quilometragem,
    cat.nome AS categoria,
    COUNT(DISTINCT l.id_locacao) AS total_locacoes,
    ROUND(COALESCE(SUM(DISTINCT l.valor_total), 0), 2) AS faturamento_gerado,
    ROUND(COALESCE((SELECT SUM(m.custo) FROM manutencoes m WHERE m.id_veiculo = v.id_veiculo), 0), 2) AS custo_manutencao,
    ROUND(
        COALESCE(SUM(DISTINCT l.valor_total), 0) - 
        COALESCE((SELECT SUM(m.custo) FROM manutencoes m WHERE m.id_veiculo = v.id_veiculo), 0)
    , 2) AS resultado_liquido
FROM veiculos v
INNER JOIN categorias cat ON v.id_categoria = cat.id_categoria
LEFT JOIN locacoes l ON v.id_veiculo = l.id_veiculo
GROUP BY v.id_veiculo, v.marca, v.modelo, v.placa, v.status, v.quilometragem, cat.nome
ORDER BY resultado_liquido DESC;
