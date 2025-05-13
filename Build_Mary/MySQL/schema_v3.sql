CREATE TABLE `utilizador` (
  `idUtilizador` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(50) NOT NULL,
  `grupo` varchar(50) NOT NULL,
  `telemovel` varchar(12) NOT NULL,
  `tipo` varchar(10) NOT NULL,
  `email` varchar(100) NOT NULL,
  `role` enum('admin','jogador') NOT NULL DEFAULT 'jogador',
  PRIMARY KEY (`idUtilizador`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `jogo` (
  `IDJogo` int(11) NOT NULL AUTO_INCREMENT,
  `idUtilizador` int(11) NOT NULL,
  `descricao` text NOT NULL,
  `inicio` timestamp NULL DEFAULT NULL,
  `fim` timestamp NULL DEFAULT NULL,
  `estado` varchar(20) NOT NULL CHECK (`estado` in ('por_iniciar','ativo','terminado')),
  PRIMARY KEY (`IDJogo`),
  KEY `idUtilizador` (`idUtilizador`),
  CONSTRAINT `jogo_ibfk_1` FOREIGN KEY (`idUtilizador`) REFERENCES `utilizador` (`idUtilizador`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `setupMaze` (
  `id_setup` int(11) NOT NULL AUTO_INCREMENT,
  `IDJogo` int(11) NOT NULL,
  `limiteRuido` float DEFAULT 21.5,
  PRIMARY KEY (`id_setup`),
  KEY `IDJogo` (`IDJogo`),
  CONSTRAINT `setupMaze_ibfk_1` FOREIGN KEY (`IDJogo`) REFERENCES `jogo` (`IDJogo`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `corridor` (
  `id_corredor` int(11) NOT NULL AUTO_INCREMENT,
  `salaA` int(11) NOT NULL,
  `salaB` int(11) NOT NULL,
  `status` enum('open','closed') DEFAULT 'open',
  `IDJogo` int(11) NOT NULL,
  PRIMARY KEY (`id_corredor`),
  UNIQUE KEY `unique_corridor` (`salaA`,`salaB`,`IDJogo`),
  KEY `IDJogo` (`IDJogo`),
  CONSTRAINT `corridor_ibfk_1` FOREIGN KEY (`IDJogo`) REFERENCES `jogo` (`IDJogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `sound` (
  `id_sound` varchar(255) NOT NULL,
  `player` int(11) NOT NULL,
  `hour` datetime NOT NULL,
  `soundLevel` float NOT NULL,
  `IDJogo` int(11) NOT NULL,
  PRIMARY KEY (`id_sound`),
  UNIQUE KEY `idx_unique_sound` (`player`,`hour`),
  KEY `IDJogo` (`IDJogo`),
  CONSTRAINT `sound_ibfk_1` FOREIGN KEY (`IDJogo`) REFERENCES `jogo` (`IDJogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `medicoesPassagens` (
  `id_medicao` varchar(255) NOT NULL,
  `player` int(11) NOT NULL,
  `marsami` int(11) NOT NULL,
  `roomOrigin` int(11) NOT NULL,
  `roomDestiny` int(11) NOT NULL,
  `status` int(11) NOT NULL CHECK (`status` in (0,1,2)),
  `IDJogo` int(11) NOT NULL,
  PRIMARY KEY (`id_medicao`),
  UNIQUE KEY `idx_unique_movement` (`player`,`marsami`,`roomOrigin`,`roomDestiny`,`status`),
  KEY `IDJogo` (`IDJogo`),
  CONSTRAINT `medicoesPassagens_ibfk_1` FOREIGN KEY (`IDJogo`) REFERENCES `jogo` (`IDJogo`),
  CONSTRAINT `medicoesPassagens_ibfk_2` FOREIGN KEY (`roomOrigin`,`roomDestiny`,`IDJogo`) REFERENCES `corridor` (`salaA`,`salaB`,`IDJogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `ocupacaoLabirinto` (
  `sala` int(11) NOT NULL,
  `odd` int(11) DEFAULT 0,
  `even` int(11) DEFAULT 0,
  `triggersUsed` int(11) DEFAULT 0,
  `IDJogo` int(11) NOT NULL,
  PRIMARY KEY (`sala`,`IDJogo`),
  KEY `IDJogo` (`IDJogo`),
  CONSTRAINT `ocupacaoLabirinto_ibfk_1` FOREIGN KEY (`IDJogo`) REFERENCES `jogo` (`IDJogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `advanced_outliers_sound` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `player_id` int(11) DEFAULT NULL,
  `soundLevel` float DEFAULT NULL,
  `hour` datetime DEFAULT NULL,
  `errorReason` varchar(255) DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  `IDJogo` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `IDJogo` (`IDJogo`),
  CONSTRAINT `advanced_outliers_sound_ibfk_1` FOREIGN KEY (`IDJogo`) REFERENCES `jogo` (`IDJogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `advanced_outliers_movements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `marsami_id` int(11) DEFAULT NULL,
  `roomOrigin` int(11) DEFAULT NULL,
  `roomDestiny` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `errorReason` varchar(255) DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  `IDJogo` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `IDJogo` (`IDJogo`),
  CONSTRAINT `advanced_outliers_movements_ibfk_1` FOREIGN KEY (`IDJogo`) REFERENCES `jogo` (`IDJogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `mensagens` (
  `id_mensagem` int(11) NOT NULL AUTO_INCREMENT,
  `IDJogo` int(11) NOT NULL,
  `tipo` enum('alerta_ruido','gatilho','erro') NOT NULL,
  `mensagem` text,
  `hora` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_mensagem`),
  KEY `IDJogo` (`IDJogo`),
  CONSTRAINT `mensagens_ibfk_1` FOREIGN KEY (`IDJogo`) REFERENCES `jogo` (`IDJogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DELIMITER $$
CREATE TRIGGER `tr_FecharPortas_SeRuidoExceder`
AFTER INSERT ON `sound`
FOR EACH ROW
BEGIN
  DECLARE limite FLOAT;
  SELECT `limiteRuido` INTO limite FROM `setupMaze` WHERE `IDJogo` = NEW.`IDJogo`;
  IF NEW.`soundLevel` > limite THEN
    UPDATE `corridor` SET `status` = 'closed' WHERE `IDJogo` = NEW.`IDJogo`;
    UPDATE `jogo` SET `estado` = 'terminado' WHERE `IDJogo` = NEW.`IDJogo`;
    INSERT INTO `mensagens` (`IDJogo`, `tipo`, `mensagem`)
    VALUES (NEW.`IDJogo`, 'alerta_ruido', 'Portas fechadas devido a ruído excessivo.');
  END IF;
END$$
DELIMITER ;