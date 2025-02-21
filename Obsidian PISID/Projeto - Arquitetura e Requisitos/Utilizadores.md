ver:
	[[A NÃO IMPLEMENTAR]]
	[[Administrador da Base de Dados]]
	[[Administrador da Aplicação]]
	[[Arquitetura]]
	[[Formulários HTML]]
	[[Jogadores]]
	[[Jogadores Tipo 1]]
	[[Jogadores Tipo 2]]
	[[Requisitos]]

- [[Administrador da Aplicação|administrador de jogo / administrador da aplicação]] (não confundir com administrador da base de dados)
	- cria e apaga [[Jogadores|jogadores]]
	- cria jogos e define os [[Parâmetros do Jogo|parâmetros dos jogos]]
	- tem acesso a uma página / interface HTML / PHP próprio que interage com a base de dados (seja diretamente por queries seja por [[Stored Procedures|SPs]])
	- pode reiniciar o processo de [[Migração de MongoDB para SQL|transferência de dados do MongoDB para o MySQL]] caso este tenha problemas ou seja interrompido
		- (considerado o plano B caso as safeguards automáticas falhem)
- [[Administrador da Base de Dados|administrador da base de dados]]
- [[Jogadores|jogador]]
	- tem a capacidade de observar e interagir com os elementos de jogo mas não tem acesso direto a nenhuma das BDs, ainda que as suas ações possam ter um impacto distanciado
	- existem dois tipos de jogadores, para efeito de simplicidade neste documento foram identificados como:
		- [[Jogadores Tipo 1]]
			- jogadores que participam no jogo através de uma [[HTML|página web]]
		- [[Jogadores Tipo 2]]
			- jogadores que participam no jogo através de uma [[Aplicação Android|aplicação Android]]
