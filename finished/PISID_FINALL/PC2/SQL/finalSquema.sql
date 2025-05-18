-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 18, 2025 at 04:42 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pisid`
--

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_UpdateRoomOccupancy` (IN `idjogo` INT, IN `marsamiNumber` INT, IN `salaOrigem` INT, IN `salaDestino` INT)   BEGIN
    DECLARE is_even BOOLEAN;
    SET is_even = MOD(marsamiNumber, 2) = 0;

    IF is_even THEN
        UPDATE ocupacaolabirinto
        SET even = GREATEST(even - 1, 0)
        WHERE sala = salaOrigem AND idjogo = idjogo;

        UPDATE ocupacaolabirinto
        SET even = even + 1
        WHERE sala = salaDestino AND idjogo = idjogo;
    ELSE
        UPDATE ocupacaolabirinto
        SET odd = GREATEST(odd - 1, 0)
        WHERE sala = salaOrigem;

        UPDATE ocupacaolabirinto
        SET odd = odd + 1
        WHERE sala = salaDestino AND idjogo = idjogo;
    END IF;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `advanced_outliers_movements`
--

CREATE TABLE `advanced_outliers_movements` (
  `id` int(11) NOT NULL,
  `marsami_id` int(11) DEFAULT NULL,
  `roomorigin` int(11) DEFAULT NULL,
  `roomdestiny` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `errorreason` varchar(255) DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  `idjogo` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `advanced_outliers_sound`
--

CREATE TABLE `advanced_outliers_sound` (
  `id` int(11) NOT NULL,
  `player_id` int(11) DEFAULT NULL,
  `soundlevel` float DEFAULT NULL,
  `hour` datetime DEFAULT NULL,
  `errorreason` varchar(255) DEFAULT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  `idjogo` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `corridor`
--

CREATE TABLE `corridor` (
  `id_corredor` int(11) NOT NULL,
  `salaa` int(11) NOT NULL,
  `salab` int(11) NOT NULL,
  `status` enum('open','closed') DEFAULT 'open',
  `idjogo` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `jogo`
--

CREATE TABLE `jogo` (
  `idjogo` int(11) NOT NULL,
  `idutilizador` int(11) NOT NULL,
  `descricao` text NOT NULL,
  `inicio` timestamp NULL DEFAULT NULL,
  `fim` timestamp NULL DEFAULT NULL,
  `estado` varchar(20) NOT NULL CHECK (`estado` in ('por_iniciar','ativo','terminado'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `jogo`
--

INSERT INTO `jogo` (`idjogo`, `idutilizador`, `descricao`, `inicio`, `fim`, `estado`) VALUES
(2, 2, 'test', NULL, NULL, 'terminado'),
(3, 2, 'test2 5555', '2025-05-17 23:14:59', NULL, 'terminado'),
(4, 2, 'test3\r\n', '2025-05-17 23:49:26', NULL, 'terminado'),
(5, 2, 'test\r\n', '2025-05-18 00:05:00', NULL, 'terminado'),
(6, 2, 'test6', '2025-05-18 00:24:50', '2025-05-18 00:24:52', 'terminado'),
(7, 2, 'test7', '2025-05-18 00:27:46', '2025-05-18 00:29:32', 'terminado'),
(8, 2, 'test8', '2025-05-18 00:31:23', '2025-05-18 00:36:45', 'terminado');

--
-- Triggers `jogo`
--
DELIMITER $$
CREATE TRIGGER `limpar_dados_quando_jogo_termina` AFTER UPDATE ON `jogo` FOR EACH ROW BEGIN
    IF NEW.estado = 'terminado' THEN
        -- Apaga primeiro da tabela ocupacaolabirinto
        DELETE FROM ocupacaolabirinto WHERE idjogo = NEW.idjogo;

        -- Depois mensagens
        DELETE FROM mensagens WHERE idjogo = NEW.idjogo;

        -- Depois sound
        DELETE FROM sound WHERE idjogo = NEW.idjogo;

        -- Depois medicoespassagens
        DELETE FROM medicoespassagens WHERE idjogo = NEW.idjogo;

        -- Depois corridor
        DELETE FROM corridor WHERE idjogo = NEW.idjogo;

        -- E por fim setupmaze
        DELETE FROM setupmaze WHERE idjogo = NEW.idjogo;
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `medicoespassagens`
--

CREATE TABLE `medicoespassagens` (
  `id_medicao` varchar(255) NOT NULL,
  `player` int(11) NOT NULL,
  `marsami` int(11) NOT NULL,
  `roomorigin` int(11) DEFAULT NULL,
  `roomdestiny` int(11) NOT NULL,
  `status` int(11) NOT NULL CHECK (`status` in (0,1,2)),
  `idjogo` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `mensagens`
--

CREATE TABLE `mensagens` (
  `id_mensagem` int(11) NOT NULL,
  `idjogo` int(11) NOT NULL,
  `leitura` decimal(10,2) NOT NULL,
  `sala` int(11) NOT NULL DEFAULT 0,
  `sensor` int(11) NOT NULL DEFAULT 0,
  `tipo` enum('alerta_ruido','gatilho','erro') NOT NULL,
  `mensagem` text DEFAULT NULL,
  `hora` timestamp NOT NULL DEFAULT current_timestamp(),
  `hora_escrita` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `ocupacaolabirinto`
--

CREATE TABLE `ocupacaolabirinto` (
  `sala` int(11) NOT NULL,
  `odd` int(11) DEFAULT 0,
  `even` int(11) DEFAULT 0,
  `triggersused` int(11) DEFAULT 0,
  `idjogo` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `setupmaze`
--

CREATE TABLE `setupmaze` (
  `id_setup` int(11) NOT NULL,
  `idjogo` int(11) NOT NULL,
  `normalnoise` decimal(10,2) DEFAULT 19.20,
  `frozentime` int(11) NOT NULL,
  `noisevartoleration` decimal(10,2) DEFAULT 2.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sound`
--

CREATE TABLE `sound` (
  `id_sound` int(255) NOT NULL,
  `player` int(11) NOT NULL,
  `hour` datetime(6) NOT NULL,
  `soundlevel` float NOT NULL,
  `idjogo` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `utilizador`
--

CREATE TABLE `utilizador` (
  `idutilizador` int(11) NOT NULL,
  `nome` varchar(50) NOT NULL,
  `grupo` varchar(50) NOT NULL,
  `telemovel` varchar(12) NOT NULL,
  `tipo` varchar(10) NOT NULL,
  `email` varchar(100) NOT NULL,
  `role` enum('admin','jogador') NOT NULL DEFAULT 'jogador'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `utilizador`
--

INSERT INTO `utilizador` (`idutilizador`, `nome`, `grupo`, `telemovel`, `tipo`, `email`, `role`) VALUES
(2, 'grupo22', '22', '999999999', 'jogador', 'grupo22@iscte-iul.pt', 'jogador');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `advanced_outliers_movements`
--
ALTER TABLE `advanced_outliers_movements`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idjogo` (`idjogo`);

--
-- Indexes for table `advanced_outliers_sound`
--
ALTER TABLE `advanced_outliers_sound`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idjogo` (`idjogo`);

--
-- Indexes for table `corridor`
--
ALTER TABLE `corridor`
  ADD PRIMARY KEY (`id_corredor`),
  ADD UNIQUE KEY `unique_corridor` (`salaa`,`salab`,`idjogo`),
  ADD KEY `idjogo` (`idjogo`);

--
-- Indexes for table `jogo`
--
ALTER TABLE `jogo`
  ADD PRIMARY KEY (`idjogo`),
  ADD KEY `idutilizador` (`idutilizador`);

--
-- Indexes for table `medicoespassagens`
--
ALTER TABLE `medicoespassagens`
  ADD PRIMARY KEY (`id_medicao`),
  ADD UNIQUE KEY `idx_unique_movement` (`player`,`marsami`,`roomorigin`,`roomdestiny`,`status`),
  ADD KEY `idjogo` (`idjogo`),
  ADD KEY `medicoespassagens_ibfk_2` (`roomorigin`,`roomdestiny`,`idjogo`);

--
-- Indexes for table `mensagens`
--
ALTER TABLE `mensagens`
  ADD PRIMARY KEY (`id_mensagem`),
  ADD KEY `idjogo` (`idjogo`);

--
-- Indexes for table `ocupacaolabirinto`
--
ALTER TABLE `ocupacaolabirinto`
  ADD PRIMARY KEY (`sala`,`idjogo`),
  ADD KEY `idjogo` (`idjogo`);

--
-- Indexes for table `setupmaze`
--
ALTER TABLE `setupmaze`
  ADD PRIMARY KEY (`id_setup`),
  ADD KEY `idjogo` (`idjogo`);

--
-- Indexes for table `sound`
--
ALTER TABLE `sound`
  ADD PRIMARY KEY (`id_sound`),
  ADD UNIQUE KEY `idx_unique_sound` (`player`,`hour`),
  ADD KEY `idjogo` (`idjogo`);

--
-- Indexes for table `utilizador`
--
ALTER TABLE `utilizador`
  ADD PRIMARY KEY (`idutilizador`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `advanced_outliers_movements`
--
ALTER TABLE `advanced_outliers_movements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=811;

--
-- AUTO_INCREMENT for table `advanced_outliers_sound`
--
ALTER TABLE `advanced_outliers_sound`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `corridor`
--
ALTER TABLE `corridor`
  MODIFY `id_corredor` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1009;

--
-- AUTO_INCREMENT for table `jogo`
--
ALTER TABLE `jogo`
  MODIFY `idjogo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `mensagens`
--
ALTER TABLE `mensagens`
  MODIFY `id_mensagem` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=396;

--
-- AUTO_INCREMENT for table `setupmaze`
--
ALTER TABLE `setupmaze`
  MODIFY `id_setup` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=74;

--
-- AUTO_INCREMENT for table `sound`
--
ALTER TABLE `sound`
  MODIFY `id_sound` int(255) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=794;

--
-- AUTO_INCREMENT for table `utilizador`
--
ALTER TABLE `utilizador`
  MODIFY `idutilizador` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `advanced_outliers_movements`
--
ALTER TABLE `advanced_outliers_movements`
  ADD CONSTRAINT `advanced_outliers_movements_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`);

--
-- Constraints for table `advanced_outliers_sound`
--
ALTER TABLE `advanced_outliers_sound`
  ADD CONSTRAINT `advanced_outliers_sound_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`);

--
-- Constraints for table `corridor`
--
ALTER TABLE `corridor`
  ADD CONSTRAINT `corridor_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`);

--
-- Constraints for table `jogo`
--
ALTER TABLE `jogo`
  ADD CONSTRAINT `jogo_ibfk_1` FOREIGN KEY (`idutilizador`) REFERENCES `utilizador` (`idutilizador`);

--
-- Constraints for table `medicoespassagens`
--
ALTER TABLE `medicoespassagens`
  ADD CONSTRAINT `medicoespassagens_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`),
  ADD CONSTRAINT `medicoespassagens_ibfk_2` FOREIGN KEY (`roomorigin`,`roomdestiny`,`idjogo`) REFERENCES `corridor` (`salaa`, `salab`, `idjogo`);

--
-- Constraints for table `mensagens`
--
ALTER TABLE `mensagens`
  ADD CONSTRAINT `mensagens_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`);

--
-- Constraints for table `ocupacaolabirinto`
--
ALTER TABLE `ocupacaolabirinto`
  ADD CONSTRAINT `ocupacaolabirinto_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`);

--
-- Constraints for table `setupmaze`
--
ALTER TABLE `setupmaze`
  ADD CONSTRAINT `setupmaze_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`);

--
-- Constraints for table `sound`
--
ALTER TABLE `sound`
  ADD CONSTRAINT `sound_ibfk_1` FOREIGN KEY (`idjogo`) REFERENCES `jogo` (`idjogo`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
