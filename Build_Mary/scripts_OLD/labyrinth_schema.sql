-- Jogo básico ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jogo (
    id_jogo INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(100) DEFAULT 'labirinto demo',
    inicio    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    fim       DATETIME,
    estado    ENUM('ativo','inativo') DEFAULT 'ativo'
);

-- Limites configuráveis por jogo (1-to-1) -------------------
CREATE TABLE IF NOT EXISTS setupMaze (
    jogo_id      INT PRIMARY KEY,
    limiteRuido  FLOAT DEFAULT 21.5,
    FOREIGN KEY (jogo_id) REFERENCES jogo(id_jogo)
);

-- Portas / corredores --------------------------------------
CREATE TABLE IF NOT EXISTS corridor (
    id_corredor INT AUTO_INCREMENT PRIMARY KEY,
    salaA INT NOT NULL,
    salaB INT NOT NULL,
    status ENUM('open','closed') DEFAULT 'open',
    jogo_id INT NOT NULL,
    FOREIGN KEY (jogo_id) REFERENCES jogo(id_jogo)
);

-- Registo do som bruto -------------------------------------
CREATE TABLE IF NOT EXISTS sound (
    id_sound  VARCHAR(64) PRIMARY KEY,
    player    INT,
    hour      DATETIME,
    soundLevel FLOAT,
    jogo_id   INT,
    FOREIGN KEY (jogo_id) REFERENCES jogo(id_jogo)
);

-- Movimentos de marsamis -----------------------------------
CREATE TABLE IF NOT EXISTS medicoesPassagens (
    id_medicao  VARCHAR(64) PRIMARY KEY,
    player      INT,
    marsami     INT,
    roomOrigin  INT,
    roomDestiny INT,
    status      TINYINT,          -- 0,1,2 como no enunciado
    jogo_id     INT,
    FOREIGN KEY (jogo_id) REFERENCES jogo(id_jogo)
);

-- Ocupação corrente das salas ------------------------------
CREATE TABLE IF NOT EXISTS ocupacaoLabirinto (
    jogo_id INT,
    sala    INT,
    odd     INT DEFAULT 0,
    even    INT DEFAULT 0,
    PRIMARY KEY (jogo_id, sala),
    FOREIGN KEY (jogo_id) REFERENCES jogo(id_jogo)
);

DELIMITER $$

-- Atualiza contagem numa sala -------------------------------
CREATE PROCEDURE sp_UpdateRoomOccupancy(
    IN p_jogo   INT,
    IN p_sala   INT,
    IN p_isOdd  BOOLEAN   -- TRUE → odd; FALSE → even
)
BEGIN
    INSERT INTO ocupacaoLabirinto (jogo_id, sala, odd, even)
    VALUES (p_jogo, p_sala, IF(p_isOdd,1,0), IF(p_isOdd,0,1))
    ON DUPLICATE KEY UPDATE
        odd  = odd  + IF(p_isOdd,1,0),
        even = even + IF(p_isOdd,0,1);
END$$


-- Inserir SOM -----------------------------------------------
CREATE PROCEDURE sp_InserirSom (
    IN p_id        VARCHAR(64),
    IN p_player    INT,
    IN p_hour      DATETIME,
    IN p_sound     FLOAT,
    IN p_jogo      INT
)
BEGIN
    DECLARE v_limite FLOAT;
    SELECT limiteRuido INTO v_limite FROM setupMaze WHERE jogo_id = p_jogo;

    INSERT INTO sound VALUES (p_id, p_player, p_hour, p_sound, p_jogo);

    -- dispara alerta / fecha portas se necessário
    IF p_sound > v_limite THEN
        -- fecha todas as portas
        UPDATE corridor SET status='closed' WHERE jogo_id = p_jogo;
        UPDATE jogo     SET estado='inativo', fim=NOW() WHERE id_jogo = p_jogo;
    END IF;
END$$


-- Inserir MOVIMENTO -----------------------------------------
CREATE PROCEDURE sp_InserirMovimento (
    IN p_id          VARCHAR(64),
    IN p_player      INT,
    IN p_marsami     INT,
    IN p_roomOrig    INT,
    IN p_roomDest    INT,
    IN p_status      TINYINT,
    IN p_jogo        INT
)
BEGIN
    INSERT INTO medicoesPassagens
    VALUES (p_id, p_player, p_marsami, p_roomOrig, p_roomDest, p_status, p_jogo);

    -- apenas status=1 conta como “passagem normal” ----------------
    IF p_status = 1 THEN
        CALL sp_UpdateRoomOccupancy(
            p_jogo,
            p_roomDest,
            MOD(p_marsami,2)    -- odd =1 / even =0
        );
    END IF;
END$$

DELIMITER ;

-- Fecha portas se som exceder o limite  ----------------------
CREATE TRIGGER tr_FecharPortas_SeRuidoExceder
AFTER INSERT ON sound
FOR EACH ROW
BEGIN
    DECLARE v_limite FLOAT;
    SELECT limiteRuido INTO v_limite FROM setupMaze WHERE jogo_id = NEW.jogo_id;

    IF NEW.soundLevel > v_limite THEN
        UPDATE corridor SET status='closed' WHERE jogo_id = NEW.jogo_id;
        UPDATE jogo SET estado='inativo', fim=NOW() WHERE id_jogo = NEW.jogo_id;
    END IF;
END;
