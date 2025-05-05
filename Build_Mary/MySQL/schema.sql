-- -----------------------------------------------------  
-- cleanup existing procedures/triggers  
-- -----------------------------------------------------  
DROP PROCEDURE IF EXISTS sp_MigrateSound;  
DROP PROCEDURE IF EXISTS sp_MigrateMovements;  
DROP PROCEDURE IF EXISTS sp_UpdateRoomOccupancy;  
DROP TRIGGER IF EXISTS tr_FecharPortas_SeRuidoExceder;  
DROP TRIGGER IF EXISTS tr_Sound_AfterInsert_RemoveDuplicate;  


-- -----------------------------------------------------  
-- cleanup existing tables  
-- ----------------------------------------------------- 
DROP TABLE IF EXISTS utilizador;
DROP TABLE IF EXISTS jogo;
DROP TABLE IF EXISTS setupmaze;
DROP TABLE IF EXISTS corridor;
DROP TABLE IF EXISTS sound;
DROP TABLE IF EXISTS medicoesPassagens;
DROP TABLE IF EXISTS ocupaçãoLabirinto;
DROP TABLE IF EXISTS marsamis;
DROP TABLE IF EXISTS localizacaoMarsami;
DROP TABLE IF EXISTS mensagens;

-- -----------------------------------------------------  
-- tables  
-- -----------------------------------------------------  
CREATE TABLE utilizador (
        utilizador_id INT PRIMARY KEY AUTO_INCREMENT,
        nome VARCHAR(50) NOT NULL,
        grupo VARCHAR(50) NOT NULL,
        telemovel VARCHAR(12) NOT NULL,
        tipo VARCHAR(10) NOT NULL,
        email VARCHAR(100) NOT NULL
);
CREATE TABLE jogo (
        IDJogo INT PRIMARY KEY AUTO_INCREMENT,
        utilizador_id INT NOT NULL,
        descricao TEXT NOT NULL,
        inicio TIMESTAMP NULL DEFAULT NULL,
        fim TIMESTAMP NULL DEFAULT NULL,
        estado VARCHAR(20) NOT NULL CHECK (
            estado IN ('por_iniciar', 'ativo', 'terminado')),
        FOREIGN KEY (utilizador_id) REFERENCES utilizador(utilizador_id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS setupmaze (  
    id_setup INT AUTO_INCREMENT PRIMARY KEY,  
    IDJogo INT NOT NULL,
    normalnoise DECIMAL NOT NULL,
    numberrooms INT NOT NULL,
    numbermarsamis INT NOT NULL,
    numberplayers INT NOT NULL,
    frozentime INT NOT NULL,
    delaytime INT NOT NULL,
    timemarsamilive INT NOT NULL,
    noisevartoleration DECIMAL NOT NULL,
    step INT NOT NULL,
    minutesstep DECIMAL,
    minutessilence DECIMAL,
    randomsound DECIMAL NOT NULL,
    randommove INT NOT NULL,
    FOREIGN KEY (IDJogo) REFERENCES jogo(IDJogo) ON DELETE CASCADE
);  

CREATE TABLE IF NOT EXISTS corridor (  
    id_corredor INT AUTO_INCREMENT PRIMARY KEY,  
    salaA INT NOT NULL,  
    salaB INT NOT NULL,  
    status ENUM('open', 'closed') DEFAULT 'open',  
    IDJogo INT NOT NULL,  
    FOREIGN KEY (IDJogo) REFERENCES jogo(IDJogo) ON DELETE CASCADE
);  

CREATE TABLE IF NOT EXISTS sound (  
    IDSound INT AUTO_INCREMENT PRIMARY KEY,    
    Hour DATETIME NOT NULL,  
    Sound FLOAT NOT NULL,  
    IDJogo INT NOT NULL,  
    FOREIGN KEY (IDJogo) REFERENCES jogo(IDJogo) ON DELETE CASCADE  
);  

CREATE TABLE IF NOT EXISTS medicoesPassagens (  
    id_medicao INT AUTO_INCREMENT PRIMARY KEY,  
    player INT NOT NULL,  
    marsami INT NOT NULL,  
    roomOrigin INT NOT NULL,  
    roomDestiny INT NOT NULL,  
    status INT NOT NULL CHECK (status IN (0, 1, 2)),  
    IDJogo INT NOT NULL,  
    FOREIGN KEY (IDJogo) REFERENCES jogo(IDJogo) ON DELETE CASCADE
);  

CREATE TABLE IF NOT EXISTS ocupaçãoLabirinto (  
    Sala INT NOT NULL,  
    NumeroMarsamisOdd INT DEFAULT 0,  
    NumeroMarsamisEven INT DEFAULT 0,  
    IDJogo INT NOT NULL,  
    PRIMARY KEY (sala, IDJogo),  
    FOREIGN KEY (IDJogo) REFERENCES jogo(IDJogo) ON DELETE CASCADE
);  

CREATE TABLE marsamis (
    marsami_id INT PRIMARY KEY,
    IDJogo INT NOT NULL,
    nome VARCHAR(50) NOT NULL,
    status TINYINT,
    FOREIGN KEY (IDJogo) REFERENCES jogo(IDJogo) ON DELETE CASCADE
);

CREATE TABLE localizacaoMarsami (
    marsami_id INT NOT NULL,
    IDJogo INT NOT NULL,
    sala INT,
    ultimaAtualizacao TIMESTAMP,
    PRIMARY KEY (marsami_id, IDJogo),
    FOREIGN KEY (IDJogo) REFERENCES jogo(IDJogo) ON DELETE CASCADE,
    FOREIGN KEY (marsami_id) REFERENCES marsamis(marsami_id) ON DELETE CASCADE
);
CREATE TABLE mensagens (
    mensagem_id INT PRIMARY KEY,
    IDJogo INT NOT NULL,
    sala INT,
    sensor INT,
    leitura DECIMAL,
    tipo_alerta VARCHAR(50),
    msg VARCHAR(100),
    hour TIMESTAMP,
    FOREIGN KEY (IDJogo) REFERENCES jogo(IDJogo) ON DELETE CASCADE
);

-- -----------------------------------------------------  
-- outlier tables  
-- -----------------------------------------------------  
CREATE TABLE IF NOT EXISTS invalid_format_errors (  
    id INT AUTO_INCREMENT PRIMARY KEY,  
    raw_payload TEXT,  
    error_message VARCHAR(255),  
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP  
);  

CREATE TABLE IF NOT EXISTS advanced_outliers_sound (  
    id INT AUTO_INCREMENT PRIMARY KEY,  
    player_id INT,  
    sound_level FLOAT,  
    hour DATETIME,  
    error_reason VARCHAR(255),  
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP  
);  

CREATE TABLE IF NOT EXISTS advanced_outliers_movements (  
    id INT AUTO_INCREMENT PRIMARY KEY,  
    marsami_id INT,  
    room_origin INT,  
    room_destiny INT,  
    status INT,  
    error_reason VARCHAR(255),  
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP  
);  


-- -----------------------------------------------------  
-- stored procedures  
-- -----------------------------------------------------  
DELIMITER $$  

CREATE PROCEDURE sp_MigrateSound(  
    IN p_id VARCHAR(255),  
    IN p_player INT,  
    IN p_hour DATETIME,  
    IN p_soundLevel FLOAT,  
    IN p_IDJogo INT  
)  
BEGIN  
    DECLARE v_limiteRuido FLOAT;  
    SELECT limiteRuido INTO v_limiteRuido FROM setupMaze WHERE IDJogo = p_IDJogo;  
    IF p_soundLevel > v_limiteRuido THEN  
        INSERT INTO advanced_outliers_sound (player_id, sound_level, hour, error_reason)  
        VALUES (p_player, p_soundLevel, p_hour, 'exceeded noise limit');  
    ELSE  
        INSERT INTO sound (id_sound, player, hour, soundLevel, IDJogo)  
        VALUES (p_id, p_player, p_hour, p_soundLevel, p_IDJogo);  
    END IF;  
END$$  

CREATE PROCEDURE sp_MigrateMovements(  
    IN p_id VARCHAR(255),  
    IN p_player INT,  
    IN p_marsami INT,  
    IN p_roomOrigin INT,  
    IN p_roomDestiny INT,  
    IN p_status INT,  
    IN p_IDJogo INT  
)  
BEGIN  
    IF p_roomOrigin = p_roomDestiny AND p_status NOT IN (0, 2) THEN  
        INSERT INTO advanced_outliers_movements  
        VALUES (p_marsami, p_roomOrigin, p_roomDestiny, p_status, 'invalid room transition', NOW());  
    ELSE  
        INSERT INTO medicoesPassagens  
        VALUES (p_id, p_player, p_marsami, p_roomOrigin, p_roomDestiny, p_status, p_IDJogo);  
    END IF;  
    IF p_status = 1 THEN  
        CALL sp_UpdateRoomOccupancy(p_roomDestiny, p_marsami % 2, p_IDJogo);  
    END IF;  
END$$  

CREATE PROCEDURE sp_UpdateRoomOccupancy(
    IN p_room INT,
    IN p_is_odd BOOLEAN,
    IN p_IDJogo INT
)
BEGIN
    INSERT INTO ocupacaoLabirinto (sala, odd, even, IDJogo)
    VALUES (p_room, p_is_odd, (1 - p_is_odd), p_IDJogo)  -- Fixed "NOT" to arithmetic
    ON DUPLICATE KEY UPDATE
        odd = odd + p_is_odd,
        even = even + (1 - p_is_odd);  -- Fixed here too
END$$

-- -----------------------------------------------------  
-- triggers  
-- -----------------------------------------------------  
CREATE TRIGGER tr_FecharPortas_SeRuidoExceder  
AFTER INSERT ON sound  
FOR EACH ROW  
BEGIN  
    DECLARE v_limiteRuido FLOAT;  
    SELECT limiteRuido INTO v_limiteRuido FROM setupMaze WHERE IDJogo = NEW.IDJogo;  
    IF NEW.soundLevel > v_limiteRuido THEN  
        UPDATE corridor SET status = 'closed' WHERE IDJogo = NEW.IDJogo;  
        UPDATE jogo SET estado = 'inativo' WHERE id_jogo = NEW.IDJogo;  
    END IF;  
END$$  

CREATE TRIGGER tr_Sound_AfterInsert_RemoveDuplicate  
AFTER INSERT ON sound  
FOR EACH ROW  
BEGIN  
    DELETE FROM sound  
    WHERE id_sound < NEW.id_sound  
    AND player = NEW.player  
    AND hour = NEW.hour;  
END$$  

DELIMITER ;  