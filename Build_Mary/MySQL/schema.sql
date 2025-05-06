-- -----------------------------------------------------  
-- cleanup existing procedures/triggers  
-- -----------------------------------------------------  
DROP PROCEDURE IF EXISTS sp_MigrateSound;  
DROP PROCEDURE IF EXISTS sp_MigrateMovements;  
DROP PROCEDURE IF EXISTS sp_UpdateRoomOccupancy;  
DROP TRIGGER IF EXISTS tr_FecharPortas_SeRuidoExceder;  
DROP TRIGGER IF EXISTS tr_Sound_AfterInsert_RemoveDuplicate;  

-- drop tables in reverse dependency order  
DROP TABLE IF EXISTS advanced_outliers_movements;  
DROP TABLE IF EXISTS advanced_outliers_sound;  
DROP TABLE IF EXISTS invalid_format_errors;  
DROP TABLE IF EXISTS ocupacaoLabirinto;  
DROP TABLE IF EXISTS medicoesPassagens;  
DROP TABLE IF EXISTS sound;  
DROP TABLE IF EXISTS corridor;  
DROP TABLE IF EXISTS setupMaze;  
DROP TABLE IF EXISTS jogo;  
DROP TABLE IF EXISTS utilizador;  

-- -----------------------------------------------------  
-- tables  
-- -----------------------------------------------------  
CREATE TABLE utilizador (
    iDUtilizador INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    grupo VARCHAR(50) NOT NULL,
    telemovel VARCHAR(12) NOT NULL,
    tipo VARCHAR(10) NOT NULL,
    email VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE jogo (
    idJogo INT PRIMARY KEY AUTO_INCREMENT,
    iDUtilizador INT NOT NULL,
    descricao TEXT NOT NULL,
    inicio TIMESTAMP NULL DEFAULT NULL,
    fim TIMESTAMP NULL DEFAULT NULL,
    estado VARCHAR(20) NOT NULL CHECK (
        estado IN ('por_iniciar', 'ativo', 'terminado')),
    FOREIGN KEY (iDUtilizador) REFERENCES utilizador(iDUtilizador)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS setupMaze (  
    id_setup INT AUTO_INCREMENT PRIMARY KEY,  
    idJogo INT NOT NULL,  
    limiteRuido FLOAT DEFAULT 21.5,  
    FOREIGN KEY (idJogo) REFERENCES jogo(idJogo)  
) ENGINE=InnoDB;  

CREATE TABLE IF NOT EXISTS corridor (  
    id_corredor INT AUTO_INCREMENT PRIMARY KEY,  
    RoomA INT NOT NULL,  
    RoomB INT NOT NULL,
    Distance INT NOT NULL,  
    status ENUM('open', 'closed') DEFAULT 'open',  
    iDJogo INT NOT NULL,  
    FOREIGN KEY (iDJogo) REFERENCES jogo(idJogo)  
) ENGINE=InnoDB;  

CREATE TABLE IF NOT EXISTS sound (  
    id_sound VARCHAR(255) PRIMARY KEY,  
    player INT NOT NULL,  
    hour DATETIME NOT NULL,  
    soundLevel FLOAT NOT NULL,  
    iDJogo INT NOT NULL,  
    FOREIGN KEY (iDJogo) REFERENCES jogo(idJogo)  
) ENGINE=InnoDB;  

CREATE TABLE IF NOT EXISTS medicoesPassagens (  
    id_medicao VARCHAR(255) PRIMARY KEY,  
    player INT NOT NULL,  
    marsami INT NOT NULL,  
    roomOrigin INT NOT NULL,  
    roomDestiny INT NOT NULL,  
    status INT NOT NULL CHECK (status IN (0, 1, 2)),  
    iDJogo INT NOT NULL,  
    FOREIGN KEY (iDJogo) REFERENCES jogo(idJogo)  
) ENGINE=InnoDB;  

CREATE TABLE IF NOT EXISTS ocupacaoLabirinto (  
    sala INT NOT NULL,  
    odd INT DEFAULT 0,  
    even INT DEFAULT 0,  
    iDJogo INT NOT NULL,  
    PRIMARY KEY (sala, iDJogo),  
    FOREIGN KEY (iDJogo) REFERENCES jogo(idJogo)  
) ENGINE=InnoDB;  

-- -----------------------------------------------------  
-- outlier tables  
-- -----------------------------------------------------  
CREATE TABLE IF NOT EXISTS invalid_format_errors (  
    id INT AUTO_INCREMENT PRIMARY KEY,  
    raw_payload TEXT,  
    error_message VARCHAR(255),  
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP  
) ENGINE=InnoDB;  

CREATE TABLE IF NOT EXISTS advanced_outliers_sound (  
    id INT AUTO_INCREMENT PRIMARY KEY,  
    player_id INT,  
    sound_level FLOAT,  
    hour DATETIME,  
    error_reason VARCHAR(255),  
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP  
) ENGINE=InnoDB;  

CREATE TABLE IF NOT EXISTS advanced_outliers_movements (  
    id INT AUTO_INCREMENT PRIMARY KEY,  
    marsami_id INT,  
    room_origin INT,  
    room_destiny INT,  
    status INT,  
    error_reason VARCHAR(255),  
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP  
) ENGINE=InnoDB;  

-- -----------------------------------------------------  
-- stored procedures  
-- -----------------------------------------------------  
DELIMITER $$  

CREATE PROCEDURE sp_MigrateSound(  
    IN p_id VARCHAR(255),  
    IN p_player INT,  
    IN p_hour DATETIME,  
    IN p_soundLevel FLOAT,  
    IN p_iDJogo INT  
)  
BEGIN  
    DECLARE v_limiteRuido FLOAT;  
    SELECT limiteRuido INTO v_limiteRuido FROM setupMaze WHERE iDJogo = p_iDJogo;  
    IF p_soundLevel > v_limiteRuido THEN  
        INSERT INTO advanced_outliers_sound (player_id, sound_level, hour, error_reason)  
        VALUES (p_player, p_soundLevel, p_hour, 'exceeded noise limit');  
    ELSE  
        INSERT INTO sound (id_sound, player, hour, soundLevel, iDJogo)  
        VALUES (p_id, p_player, p_hour, p_soundLevel, p_iDJogo);  
    END IF;  
END$$  

CREATE PROCEDURE sp_MigrateMovements(  
    IN p_id VARCHAR(255),  
    IN p_player INT,  
    IN p_marsami INT,  
    IN p_roomOrigin INT,  
    IN p_roomDestiny INT,  
    IN p_status INT,  
    IN p_iDJogo INT  
)  
BEGIN  
    IF p_roomOrigin = p_roomDestiny AND p_status NOT IN (0, 2) THEN  
        INSERT INTO advanced_outliers_movements  
        VALUES (p_marsami, p_roomOrigin, p_roomDestiny, p_status, 'invalid room transition', NOW());  
    ELSE  
        INSERT INTO medicoesPassagens  
        VALUES (p_id, p_player, p_marsami, p_roomOrigin, p_roomDestiny, p_status, p_iDJogo);  
    END IF;  
    IF p_status = 1 THEN  
        CALL sp_UpdateRoomOccupancy(p_roomDestiny, p_marsami % 2, p_iDJogo);  
    END IF;  
END$$  

CREATE PROCEDURE sp_UpdateRoomOccupancy(
    IN p_room INT,
    IN p_is_odd BOOLEAN,
    IN p_iDJogo INT
)
BEGIN
    INSERT INTO ocupacaoLabirinto (sala, odd, even, iDJogo)
    VALUES (p_room, p_is_odd, (1 - p_is_odd), p_iDJogo)
    ON DUPLICATE KEY UPDATE
        odd = odd + p_is_odd,
        even = even + (1 - p_is_odd);
END$$

-- -----------------------------------------------------  
-- triggers  
-- -----------------------------------------------------  
CREATE TRIGGER tr_FecharPortas_SeRuidoExceder  
AFTER INSERT ON sound  
FOR EACH ROW  
BEGIN  
    DECLARE v_limiteRuido FLOAT;  
    SELECT limiteRuido INTO v_limiteRuido FROM setupMaze WHERE iDJogo = NEW.iDJogo;  
    IF NEW.soundLevel > v_limiteRuido THEN  
        UPDATE corridor SET status = 'closed' WHERE iDJogo = NEW.iDJogo;  
        UPDATE jogo SET estado = 'terminado' WHERE idJogo = NEW.iDJogo;  -- Changed to idJogo
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