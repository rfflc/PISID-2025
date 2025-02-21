ver:
	[[Enunciado]]
	[[Java?]]
	[[Python]]
	[[MQTT]]
	[[MongoDB]]
	[[Projeto - Tecnologias/SQL]]
	[[Migração de MongoDB para SQL]]
	[[Servidor Remoto]]
	[[PC1]]
	[[PC2]]
	[[Jogadores]]
	[[Jogadores Tipo 1]]
	[[Jogadores Tipo 2]]

![[Screenshot 2025-02-18 at 01.03.59.png]]
a arquitetura do projeto como ilustrada no enunciado

(aconselha-se a cuidada observação do diagrama dada a sua natureza densa)

Descrição geral do funcionamento:

- Sensores simulados no [[Servidor Remoto|servidor remoto]] enviam os sinais gerados para o [[PC1]] que contém a base de dados não-relacional feita no [[MongoDB]] através de [[MQTT]] com [[Java?]] ou [[Python]].

- Uma camada de software depois faz a [[Migração de MongoDB para SQL|tratamento e migração de dados do MongoDB para o MySQL]] cuja base de dados se encontra no [[PC2]].

- Uma camada com [[HTML]] depois faz a comunicação com [[Jogadores Tipo 1|jogadores que se ligam por uma página web]].

- Uma camada paralela que utiliza [[Java?]] ou [[Python]], [[MQTT]] e [[PHP]] faz a comunicação equivalente com [[Jogadores Tipo 2|jogadores que se ligam pela aplicação Android]].

- Estas duas camadas são responsáveis pela interação dos [[Jogadores|jogadores]] com o jogo. Isto inclui a comunicação dos [[Regras do Jogo|valores relevantes ao jogo]] a cada jogador, assim como a comunicação das interações do jogador através dos [[Atuadores|atuadores]] e do [[Gatilho|gatilho]] de volta para o servidor remoto.

- Uma última camada que por sua vez comunica com o PC2 através de Java ou Python, completa o ciclo.

