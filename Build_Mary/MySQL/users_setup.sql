-- users_setup.sql
CREATE USER 'service_script_migration'@'localhost' IDENTIFIED BY 'pisid';
GRANT INSERT, UPDATE ON maze.medicoespassagens TO 'service_script_migration'@'localhost';
GRANT INSERT, UPDATE ON maze.sound TO 'service_script_migration'@'localhost';

CREATE USER 'service_script_cloud'@'localhost' IDENTIFIED BY 'pisid';
GRANT SELECT, UPDATE ON maze.corridor TO 'service_script_cloud'@'localhost';
GRANT SELECT, UPDATE ON maze.ocupacaolabirinto TO 'service_script_cloud'@'localhost';
GRANT INSERT ON maze.mensagens TO 'service_script_cloud'@'localhost';

CREATE USER 'web_user'@'localhost' IDENTIFIED BY 'pisid';
GRANT SELECT ON maze.jogo TO 'web_user'@'localhost';
GRANT SELECT ON maze.ocupacaolabirinto TO 'web_user'@'localhost';
GRANT SELECT ON maze.mensagens TO 'web_user'@'localhost';

FLUSH PRIVILEGES;