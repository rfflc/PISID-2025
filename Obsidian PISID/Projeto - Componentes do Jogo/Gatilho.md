ver:
	[[Gráfico do Labirinto]]
	[[Marsamis]]
	[[Pontuação]]
	[[Regras do Jogo]]
	[[Sensores de Movimento]]
	[[Sensores de Entrada]]
	[[Sensores de Saída]]

- é efetivamente o mecanismo pelo qual os [[Jogadores|jogadores]] podem [[Pontuação|marcar pontos]]
	- presente em alguma forma para [[Jogadores Tipo 1|jogadores web]] e [[Jogadores Tipo 2|jogadores Android]]
	- consiste num botão que pode ser ativado pelo jogador quando este deteta que o número de [[Marsamis|odds e evens]] é igual numa dada sala do seu [[Labirintos|labirinto]]
		- ativar este botão no momento certo ganha 1 ponto ao jogador, ao passo que falhar o momento resulta numa perda de 1/2 ponto
	- a ativação do botão resulta numa emissão de sinal para o [[PC2]] para que este possa calcular, registar e refletir as alterações na pontuação do jogador
		- esta emissão será feita através de [[HTML]] ou [[PHP]] para jogadores web e através de [[Java?]] ou [[Python]] (com [[MQTT]] ou não) no caso de  jogadores Android
