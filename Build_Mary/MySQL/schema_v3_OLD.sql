CREATE TABLE `utilizador` (
  `idutilizador` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(50) NOT NULL,
  `grupo` varchar(50) NOT NULL,
  `telemovel` varchar(12) NOT NULL,
  `tipo` varchar(10) NOT NULL,
  `email` varchar(100) NOT NULL,
  `role` enum('admin','jogador') NOT NULL DEFAULT 'jogador',
  PRIMARY KEY (`idutilizador`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `jogo` (
  `idjogo` int(11) NOT NULL AUTO_INCREMENT,
  `idutilizador` int(11) NOT NULL,
  `descricao` text NOT NULL,
  `inicio` timestamp NULL DEFAULT NULL,
  `fim` timestamp NULL DEFAULT NULL,
  `estado` varchar(20) NOT NULL CHECK (`estado` in ('por_iniciar','ativo','terminado')),
  PRIMARY KEY (`idjogo`),
  KEY `idutilizador` (`idutilizador`),
  CONSTRAINT `jogo_ibfk_1` FOREIGN KEY (`idutilizador`) REFERENCES `utilizador` (`idutilizador`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `setupmaze` (
  `id_setup` int(11) NOT NULL AUTO_INCREMENT,
  `idjogo` int(11) NOT NULL,
  `limiteruido` float DEFAULT 21.5,
  PRIMARY KEY (`id_setup`),
  KEY `idjogo` (`idjogo`),
  CONSTRAINT `setupmaze_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `corridor` (
  `id_corredor` int(11) NOT NULL AUTO_INCREMENT,
  `salaa` int(11) NOT NULL,
  `salab` int(11) NOT NULL,
  `status` enum('open','closed') DEFAULT 'open',
  `idjogo` int(11) NOT NULL,
  PRIMARY KEY (`id_corredor`),
  UNIQUE KEY `unique_corridor` (`salaa`,`salab`,`idjogo`),
  KEY `idjogo` (`idjogo`),
  CONSTRAINT `corridor_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `sound` (
  `id_sound` varchar(255) NOT NULL,
  `player` int(11) NOT NULL,
  `hour` datetime NOT NULL,
  `soundlevel` float NOT NULL,
  `idjogo` int(11) NOT NULL,
  PRIMARY KEY (`id_sound`),
  UNIQUE KEY `idx_unique_sound` (`player`,`hour`),
  KEY `idjogo` (`idjogo`),
  CONSTRAINT `sound_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `medicoespassagens` (
  `id_medicao` varchar(255) NOT NULL,
  `player` int(11) NOT NULL,
  `marsami` int(11) NOT NULL,
  `roomorigin` int(11) NOT NULL,
  `roomdestiny` int(11) NOT NULL,
  `status` int(11) NOT NULL CHECK (`status` in (0,1,2)),
  `idjogo` int(11) NOT NULL,
  PRIMARY KEY (`id_medicao`),
  UNIQUE KEY `idx_unique_movement` (`player`,`marsami`,`roomorigin`,`roomdestiny`,`status`),
  KEY `idjogo` (`idjogo`),
  CONSTRAINT `medicoespassagens_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`),
  CONSTRAINT `medicoespassagens_ibfk_2` FOREIGN KEY (`roomorigin`,`roomdestiny`,`idjogo`) REFERENCES `corridor` (`salaa`,`salab`,`idjogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `ocupacaolabirinto` (
  `sala` int(11) NOT NULL,
  `odd` int(11) DEFAULT 0,
  `even` int(11) DEFAULT 0,
  `triggersused` int(11) DEFAULT 0,
  `idjogo` int(11) NOT NULL,
  PRIMARY KEY (`sala`,`idjogo`),
  KEY `idjogo` (`idjogo`),
  CONSTRAINT `ocupacaolabirinto_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `advanced_outliers_sound` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `player_id` int(11) DEFAULT NULL,
  `soundlevel` float DEFAULT NULL,
  `hour` datetime DEFAULT NULL,
  `errorreason` varchar(255) DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  `idjogo` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idjogo` (`idjogo`),
  CONSTRAINT `advanced_outliers_sound_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `advanced_outliers_movements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `marsami_id` int(11) DEFAULT NULL,
  `roomorigin` int(11) DEFAULT NULL,
  `roomdestiny` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `errorreason` varchar(255) DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  `idjogo` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idjogo` (`idjogo`),
  CONSTRAINT `advanced_outliers_movements_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `mensagens` (
  `id_mensagem` int(11) NOT NULL AUTO_INCREMENT,
  `idjogo` int(11) NOT NULL,
  `tipo` enum('alerta_ruido','gatilho','erro') NOT NULL,
  `mensagem` text,
  `hora` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_mensagem`),
  KEY `idjogo` (`idjogo`),
  CONSTRAINT `mensagens_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DELIMITER $$
CREATE TRIGGER `tr_fecharportas_seruidoexceder`
AFTER INSERT ON `sound`
FOR EACH ROW
BEGIN
  DECLARE limite FLOAT;
  SELECT `limiteruido` INTO limite FROM `setupmaze` WHERE `idjogo` = NEW.`idjogo`;
  IF NEW.`soundlevel` > limite THEN
    UPDATE `corridor` SET `status` = 'closed' WHERE `idjogo` = NEW.`idjogo`;
    UPDATE `jogo` SET `estado` = 'terminado' WHERE `idjogo` = NEW.`idjogo`;
    INSERT INTO `mensagens` (`idjogo`, `tipo`, `mensagem`)
    VALUES (NEW.`idjogo`, 'alerta_ruido', 'Portas fechadas devido a ruído excessivo.');
  END IF;
END$$
DELIMITER ;