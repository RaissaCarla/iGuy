-- =====================================================================
-- SCHEMA: App de Acompanhantes / Companhia (iGuy)
-- SGBD: MySQL (8.0+)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS db_iGuy;
USE db_iGuy;

-- =====================================================================
-- 1. GESTÃO DE USUÁRIOS E PERFIS
-- =====================================================================

CREATE TABLE usuarios (
    id_usuario VARCHAR(36) DEFAULT (UUID()) PRIMARY KEY,
    nome_completo VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    telefone VARCHAR(20) NOT NULL,
    tipo_perfil ENUM('CLIENTE', 'ACOMPANHANTE') NOT NULL,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_cpf   ON usuarios(cpf);

CREATE TABLE perfis_acompanhante (
    id_acompanhante VARCHAR(36) PRIMARY KEY,
    foto_rosto VARCHAR(500),
    status_verificacao ENUM('PENDENTE', 'APROVADO', 'BLOQUEADO') NOT NULL DEFAULT 'PENDENTE',
    nota_media DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    is_online BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (id_acompanhante) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE INDEX idx_perfis_acompanhante_status  ON perfis_acompanhante(status_verificacao);
CREATE INDEX idx_perfis_acompanhante_online  ON perfis_acompanhante(is_online);

CREATE TABLE contatos_emergencia (
    id_contato INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente VARCHAR(36) NOT NULL,
    nome VARCHAR(150) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    parentesco VARCHAR(50),
    FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE INDEX idx_contatos_emergencia_cliente ON contatos_emergencia(id_cliente);

-- =====================================================================
-- 2. SERVIÇOS E HABILIDADES (SELOS)
-- =====================================================================

CREATE TABLE categorias_servico (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    preco_base_hora DECIMAL(10,2) NOT NULL CHECK (preco_base_hora >= 0)
);

INSERT INTO categorias_servico (titulo, preco_base_hora) VALUES
('Companhia', 30.00),
('Acompanhamento médico', 40.00),
('Apoio burocrático', 35.00),
('Serviços do dia a dia', 25.00);

CREATE TABLE selos_certificacao (
    id_selo INT AUTO_INCREMENT PRIMARY KEY,
    nome_selo VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE acompanhante_selos (
    id_acompanhante VARCHAR(36) NOT NULL,
    id_selo INT NOT NULL,
    PRIMARY KEY (id_acompanhante, id_selo),
    FOREIGN KEY (id_acompanhante) REFERENCES perfis_acompanhante(id_acompanhante) ON DELETE CASCADE,
    FOREIGN KEY (id_selo) REFERENCES selos_certificacao(id_selo) ON DELETE CASCADE
);

-- =====================================================================
-- 3. SOLICITAÇÕES (CICLO DE VIDA DO SERVIÇO)
-- =====================================================================

CREATE TABLE solicitacoes (
    id_solicitacao VARCHAR(36) DEFAULT (UUID()) PRIMARY KEY,
    id_cliente VARCHAR(36) NOT NULL,
    id_acompanhante VARCHAR(36),
    id_categoria INT NOT NULL,
    status ENUM('BUSCANDO', 'ACEITO', 'EM_DESLOCAMENTO', 'EM_ANDAMENTO', 'CONCLUIDO', 'CANCELADO') NOT NULL DEFAULT 'BUSCANDO',
    data_hora_agendada DATETIME NOT NULL,
    endereco_origem VARCHAR(255) NOT NULL,
    endereco_destino VARCHAR(255),
    codigo_seguranca_pin SMALLINT CHECK (codigo_seguranca_pin BETWEEN 1000 AND 9999),
    valor_total DECIMAL(10,2) CHECK (valor_total >= 0),
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_acompanhante) REFERENCES perfis_acompanhante(id_acompanhante),
    FOREIGN KEY (id_categoria) REFERENCES categorias_servico(id_categoria)
);

CREATE INDEX idx_solicitacoes_cliente      ON solicitacoes(id_cliente);
CREATE INDEX idx_solicitacoes_acompanhante ON solicitacoes(id_acompanhante);
CREATE INDEX idx_solicitacoes_status       ON solicitacoes(status);
CREATE INDEX idx_solicitacoes_data         ON solicitacoes(data_hora_agendada);

-- =====================================================================
-- 4. FINALIZAÇÃO E HISTÓRICO
-- =====================================================================

CREATE TABLE relatorios_visita (
    id_relatorio INT AUTO_INCREMENT PRIMARY KEY,
    id_solicitacao VARCHAR(36) NOT NULL,
    texto_relatorio TEXT NOT NULL,
    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_solicitacao) REFERENCES solicitacoes(id_solicitacao) ON DELETE CASCADE
);

CREATE INDEX idx_relatorios_visita_solicitacao ON relatorios_visita(id_solicitacao);

CREATE TABLE avaliacoes (
    id_avaliacao INT AUTO_INCREMENT PRIMARY KEY,
    id_solicitacao VARCHAR(36) NOT NULL,
    id_avaliador VARCHAR(36) NOT NULL,
    id_avaliado VARCHAR(36) NOT NULL,
    nota SMALLINT NOT NULL CHECK (nota BETWEEN 1 AND 5),
    comentario TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id_solicitacao, id_avaliador),
    FOREIGN KEY (id_solicitacao) REFERENCES solicitacoes(id_solicitacao) ON DELETE CASCADE,
    FOREIGN KEY (id_avaliador) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_avaliado) REFERENCES usuarios(id_usuario)
);


CREATE INDEX idx_avaliacoes_avaliado ON avaliacoes(id_avaliado);

-- =====================================================================
-- TRIGGERS: manter nota_media do acompanhante atualizada
-- =====================================================================

DELIMITER //

CREATE TRIGGER trg_atualizar_nota_media_insert
AFTER INSERT ON avaliacoes
FOR EACH ROW
BEGIN
    UPDATE perfis_acompanhante
    SET nota_media = (
        SELECT COALESCE(AVG(nota), 0)
        FROM avaliacoes
        WHERE id_avaliado = NEW.id_avaliado
    )
    WHERE id_acompanhante = NEW.id_avaliado;
END //

CREATE TRIGGER trg_atualizar_nota_media_update
AFTER UPDATE ON avaliacoes
FOR EACH ROW
BEGIN
    UPDATE perfis_acompanhante
    SET nota_media = (
        SELECT COALESCE(AVG(nota), 0)
        FROM avaliacoes
        WHERE id_avaliado = NEW.id_avaliado
    )
    WHERE id_acompanhante = NEW.id_avaliado;
END //

DELIMITER ;
