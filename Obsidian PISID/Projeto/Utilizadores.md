ver:
	[[A NÃO IMPLEMENTAR]]
	[[Administrador da Base de Dados]]
	[[Administrador de Jogos]]
	[[Arquitetura]]
	[[Formulários HTML]]
	[[Jogadores]]
	[[Jogador tipo 1]]
	[[Jogador tipo 2]]
	[[Requisitos]]

- [[Administrador de Jogos|administrador de jogo / administrador da aplicação]] (não confundir com administrador da base de dados)
	- cria e apaga [[Jogadores|jogadores]]
	- cria jogos e define os [[Parâmetros dos jogos|parâmetros dos jogos]]
	- tem acesso a uma página / interface HTML / PHP próprio que interage com a base de dados (seja diretamente por queries seja por [[Stored Procedures|SPs]])
	- pode reiniciar o processo de [[Migração de MongoDB para SQL|transferência de dados do MongoDB para o MySQL]] caso este tenha problemas ou seja interrompido
		- (considerado o plano B caso as safeguards automáticas falhem)
- [[Administrador da Base de Dados|administrador da base de dados]]