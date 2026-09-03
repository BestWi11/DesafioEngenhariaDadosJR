-- ====================================================================
-- Script DML: Povoamento Inicial com Dados Realistas (Seed)
-- Locadora de Veículos Analytics
-- ====================================================================

-- 1. Inserção de Categorias
INSERT OR IGNORE INTO categorias (id_categoria, nome, descricao, valor_diaria_base) VALUES
(1, 'Economico', 'Veiculos compactos, 1.0, ar condicionado e direcao hidraulica', 110.00),
(2, 'Seda Compacto', 'Veiculos com porta-malas amplo, motor 1.6, conforto para viagens', 160.00),
(3, 'SUV Urbano', 'Veiculos utilitarios esportivos, posicao alta de dirigir e seguranca', 230.00),
(4, 'Seda Premium', 'Veiculos executivos, acabamento refinado e cambio automatico', 350.00),
(5, 'Utilitario / Picape', 'Veiculos para carga leve, trabalho ou terrenos acidentados', 280.00);

-- 2. Inserção de Clientes (8 clientes com dados completos)
INSERT OR IGNORE INTO clientes (id_cliente, nome, cpf, cnh, telefone, email, cidade, estado, data_cadastro) VALUES
(1, 'Carlos Eduardo Silva', '111.222.333-44', '12345678901', '(11) 98765-4321', 'carlos.silva@email.com', 'Sao Paulo', 'SP', '2024-01-15 10:30:00'),
(2, 'Mariana Souza Santos', '222.333.444-55', '23456789012', '(21) 99887-7665', 'mariana.souza@email.com', 'Rio de Janeiro', 'RJ', '2024-02-01 14:20:00'),
(3, 'Rodrigo Albuquerque Lima', '333.444.555-66', '34567890123', '(31) 98877-6655', 'rodrigo.lima@email.com', 'Belo Horizonte', 'MG', '2024-02-10 09:15:00'),
(4, 'Beatriz Ferreira Costa', '444.555.666-77', '45678901234', '(41) 97766-5544', 'beatriz.costa@email.com', 'Curitiba', 'PR', '2024-03-05 16:45:00'),
(5, 'Fernando Mendes Rocha', '555.666.777-88', '56789012345', '(51) 96655-4433', 'fernando.rocha@email.com', 'Porto Alegre', 'RS', '2024-03-12 11:00:00'),
(6, 'Juliana Andrade Paiva', '666.777.888-99', '67890123456', '(71) 95544-3322', 'juliana.paiva@email.com', 'Salvador', 'BA', '2024-04-02 08:30:00'),
(7, 'Lucas Gabriel Martins', '777.888.999-00', '78901234567', '(61) 94433-2211', 'lucas.martins@email.com', 'Brasilia', 'DF', '2024-04-18 13:10:00'),
(8, 'Camila Nogueira Ribeiro', '888.999.000-11', '89012345678', '(85) 93322-1100', 'camila.ribeiro@email.com', 'Fortaleza', 'CE', '2024-05-01 17:00:00');

-- 3. Inserção de Veículos (12 veículos com diferentes status e quilometragens)
INSERT OR IGNORE INTO veiculos (id_veiculo, id_categoria, marca, modelo, ano, placa, cor, status, quilometragem) VALUES
(1, 1, 'Chevrolet', 'Onix 1.0', 2023, 'BRA2E19', 'Branco', 'Disponivel', 18500),
(2, 1, 'Hyundai', 'HB20 Sense', 2023, 'RJA4B22', 'Prata', 'Alugado', 24200),
(3, 1, 'Fiat', 'Mobi Like', 2022, 'MGX7H88', 'Vermelho', 'Disponivel', 36000),
(4, 2, 'Volkswagen', 'Virtus 1.6 MSI', 2023, 'SPK9L10', 'Cinza', 'Disponivel', 29800),
(5, 2, 'Chevrolet', 'Onix Plus Premier', 2024, 'PRQ3D55', 'Preto', 'Alugado', 11500),
(6, 3, 'Jeep', 'Compass Longitude', 2023, 'RSB8K44', 'Branco', 'Disponivel', 31200),
(7, 3, 'Hyundai', 'Creta Ultimate', 2024, 'BAZ1M99', 'Azul', 'Alugado', 14000),
(8, 3, 'Volkswagen', 'T-Cross Highline', 2023, 'DFL5N23', 'Prata', 'Manutencao', 42000),
(9, 4, 'Toyota', 'Corolla Altis Hybrid', 2024, 'CEY6P77', 'Preto', 'Disponivel', 8900),
(10, 4, 'BMW', '320i M Sport', 2023, 'BRW9Q11', 'Branco', 'Disponivel', 19400),
(11, 5, 'Toyota', 'Hilux CD SRX', 2023, 'AGR4R88', 'Prata', 'Alugado', 48500),
(12, 5, 'Fiat', 'Toro Volcano Diesel', 2023, 'RSC2T33', 'Vermelho', 'Disponivel', 33700);

-- 4. Inserção de Locações (16 locações entre finalizadas e ativas com cálculo de valores)
INSERT OR IGNORE INTO locacoes (id_locacao, id_cliente, id_veiculo, data_locacao, data_devolucao_prevista, data_devolucao_real, valor_diaria, valor_total, status) VALUES
(1, 1, 1, '2024-01-20', '2024-01-25', '2024-01-25', 110.00, 550.00, 'Finalizada'),
(2, 2, 6, '2024-02-05', '2024-02-12', '2024-02-12', 230.00, 1610.00, 'Finalizada'),
(3, 3, 4, '2024-02-15', '2024-02-20', '2024-02-20', 160.00, 800.00, 'Finalizada'),
(4, 4, 9, '2024-03-08', '2024-03-15', '2024-03-15', 350.00, 2450.00, 'Finalizada'),
(5, 1, 6, '2024-03-20', '2024-03-27', '2024-03-27', 230.00, 1610.00, 'Finalizada'),
(6, 5, 11, '2024-03-25', '2024-04-04', '2024-04-04', 280.00, 2800.00, 'Finalizada'),
(7, 6, 2, '2024-04-05', '2024-04-10', '2024-04-10', 110.00, 550.00, 'Finalizada'),
(8, 7, 10, '2024-04-20', '2024-04-23', '2024-04-23', 350.00, 1050.00, 'Finalizada'),
(9, 8, 3, '2024-05-02', '2024-05-08', '2024-05-08', 110.00, 660.00, 'Finalizada'),
(10, 2, 9, '2024-05-10', '2024-05-17', '2024-05-17', 350.00, 2450.00, 'Finalizada'),
(11, 3, 12, '2024-05-15', '2024-05-22', '2024-05-22', 280.00, 1960.00, 'Finalizada'),
(12, 4, 1, '2024-05-25', '2024-05-30', '2024-05-30', 110.00, 550.00, 'Finalizada'),
-- Locações ativas em andamento:
(13, 5, 2, '2024-06-01', '2024-06-10', NULL, 110.00, 990.00, 'Ativa'),
(14, 1, 5, '2024-06-02', '2024-06-09', NULL, 160.00, 1120.00, 'Ativa'),
(15, 6, 7, '2024-06-03', '2024-06-13', NULL, 230.00, 2300.00, 'Ativa'),
(16, 7, 11, '2024-06-04', '2024-06-14', NULL, 280.00, 2800.00, 'Ativa');

-- 5. Inserção de Manutenções Preventivas e Corretivas
INSERT OR IGNORE INTO manutencoes (id_manutencao, id_veiculo, data_manutencao, tipo_servico, custo, descricao) VALUES
(1, 1, '2024-02-10', 'Preventiva', 350.00, 'Troca de oleo, filtro de oleo e filtro de ar aos 10.000 km'),
(2, 3, '2024-03-01', 'Corretiva', 620.00, 'Substituicao de pastilhas de freio e alinhamento/balanceamento'),
(3, 6, '2024-03-15', 'Preventiva', 850.00, 'Revisao periodica de 30.000 km na concessionaria'),
(4, 8, '2024-05-28', 'Corretiva', 1400.00, 'Troca da correia dentada e reparo no sistema de arrefecimento'),
(5, 11, '2024-04-10', 'Preventiva', 1100.00, 'Revisao de 40.000 km, troca de fluidos e lubrificacao'),
(6, 4, '2024-04-25', 'Preventiva', 420.00, 'Troca de oleo sintético e filtro de combustivel');
