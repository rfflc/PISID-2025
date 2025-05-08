CREATE TABLE `utilizador` (
  `idUtilizador` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(50) NOT NULL,
  `grupo` varchar(50) NOT NULL,
  `telemovel` varchar(12) NOT NULL,
  `tipo` varchar(10) NOT NULL,
  `email` varchar(100) NOT NULL,
  PRIMARY KEY (`idUtilizador`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `jogo` (
  `idJogo` int(11) NOT NULL AUTO_INCREMENT,
  `idUtilizador` int(11) NOT NULL,
  `descricao` text NOT NULL,
  `inicio` timestamp NULL DEFAULT NULL,
  `fim` timestamp NULL DEFAULT NULL,
  `estado` varchar(20) NOT NULL CHECK (`estado` in ('por_iniciar','ativo','terminado')),
  PRIMARY KEY (`idJogo`),
  KEY `idUtilizador` (`idUtilizador`),
  CONSTRAINT `jogo_ibfk_1` FOREIGN KEY (`idUtilizador`) REFERENCES `utilizador` (`idUtilizador`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `setupmaze` (
  `id_setup` int(11) NOT NULL AUTO_INCREMENT,
  `jogo_id` int(11) NOT NULL,
  `limiteRuido` float DEFAULT 21.5,
  PRIMARY KEY (`id_setup`),
  KEY `jogo_id` (`jogo_id`),
  CONSTRAINT `setupmaze_ibfk_1` FOREIGN KEY (`jogo_id`) REFERENCES `jogo` (`idJogo`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `corridor` (
  `id_corredor` int(11) NOT NULL AUTO_INCREMENT,
  `salaA` int(11) NOT NULL,
  `salaB` int(11) NOT NULL,
  `status` enum('open','closed') DEFAULT 'open',
  `jogo_id` int(11) NOT NULL,
  PRIMARY KEY (`id_corredor`),
  KEY `jogo_id` (`jogo_id`),
  CONSTRAINT `corridor_ibfk_1` FOREIGN KEY (`jogo_id`) REFERENCES `jogo` (`idJogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `sound` (
  `id_sound` varchar(255) NOT NULL,
  `player` int(11) NOT NULL,
  `hour` datetime NOT NULL,
  `soundLevel` float NOT NULL,
  `jogo_id` int(11) NOT NULL,
  PRIMARY KEY (`id_sound`),
  UNIQUE KEY `idx_unique_sound` (`player`,`hour`),
  KEY `jogo_id` (`jogo_id`),
  CONSTRAINT `sound_ibfk_1` FOREIGN KEY (`jogo_id`) REFERENCES `jogo` (`idJogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `medicoespassagens` (
  `id_medicao` varchar(255) NOT NULL,
  `player` int(11) NOT NULL,
  `marsami` int(11) NOT NULL,
  `roomOrigin` int(11) NOT NULL,
  `roomDestiny` int(11) NOT NULL,
  `status` int(11) NOT NULL CHECK (`status` in (0,1,2)),
  `jogo_id` int(11) NOT NULL,
  PRIMARY KEY (`id_medicao`),
  UNIQUE KEY `idx_unique_movement` (`player`,`marsami`,`roomOrigin`,`roomDestiny`,`status`),
  KEY `jogo_id` (`jogo_id`),
  CONSTRAINT `medicoespassagens_ibfk_1` FOREIGN KEY (`jogo_id`) REFERENCES `jogo` (`idJogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `ocupacaolabirinto` (
  `sala` int(11) NOT NULL,
  `odd` int(11) DEFAULT 0,
  `even` int(11) DEFAULT 0,
  `jogo_id` int(11) NOT NULL,
  PRIMARY KEY (`sala`,`jogo_id`),
  KEY `jogo_id` (`jogo_id`),
  CONSTRAINT `ocupacaolabirinto_ibfk_1` FOREIGN KEY (`jogo_id`) REFERENCES `jogo` (`idJogo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `advanced_outliers_sound` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `player_id` int(11) DEFAULT NULL,
  `sound_level` float DEFAULT NULL,
  `hour` datetime DEFAULT NULL,
  `error_reason` varchar(255) DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `advanced_outliers_movements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `marsami_id` int(11) DEFAULT NULL,
  `room_origin` int(11) DEFAULT NULL,
  `room_destiny` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `error_reason` varchar(255) DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;