ver:
	[[A NÃO IMPLEMENTAR]]
	[[Arquitetura]]
	[[Regras do Jogo]]

- [[A NÃO IMPLEMENTAR|não implementar]] os [[Formulários HTML|formulários HTML]] do [[Administrador da Aplicação|administrador de jogo]]
- implementar formulários HTML para o [[Jogadores|jogador]] com:
	- login
	- criar jogo
	- iniciar jogo
- o jogador não deve, nunca, poder alterar [[Parâmetros do Jogo|parâmetros de jogos]] ativos / a decorrer
- o jogador não deve, nunca, poder alterar chaves primárias ou estrangeiras nas [[Tabelas|tabelas]]
- todos as alterações de tabelas feitas fora dos dois perfis descritos acima devem ser feitos diretamente na [[PC2|BD]] ou então feitas a partir de [[Stored Procedures|SPs]]
- o jogo inicia quando o botão "iniciar" é pressionado pelo administrador de jogo (criar páginas para os diferentes elementos / páginas de UI [[Lista de Tarefas]])
- o jogo termina automaticamente quando todos os [[Marsamis|marsamis]] atingem [[Condições de Final de Jogo|exaustão]], o [[Ruído|limite de ruído]] foi atingido em todos os [[Labirintos|labirintos]], ou quando todos os corredores apresentam o estado = 2 (que é? [[Perguntas para a Próxima Reunião com o Docente]])
- os dados dos sensores apenas são armazenados durante o jogo e podem ser descartados após o término (do jogo? da ronda?) [[Perguntas para a Próxima Reunião com o Docente]]
- a [[Aplicação Android|aplicação Android]] deve apresentar um gráfico com:
	- o número de [[Marsamis|odds e evens]] em cada [[Salas|sala]]
	- o nível de ruído
	- os botões de interação ([[Atuadores|atuadores]] e [[Gatilho|gatilho]])