ver:
	[[Android]]
	[[Aplicação Android]]
	[[Atuadores]]
	[[Condições de Final de Jogo]]
	[[Corredores]]
	[[Exaustão]]
	[[Gráfico do Labirinto]]
	[[Jogadores]]
	[[Jogadores Android]]
	[[Marsamis]]
	[[Portas]]
	[[Regras do Jogo]]
	[[Salas]]
	[[Sensores de Movimento]]
	[[Sensores de Entrada]]
	[[Sensores de Saída]] ^cb581d
	[[Status]]

- [[Sensores de Movimento|sensores de movimento]] que simulam os movimentos dos [[Marsamis|marsamis]] no [[Labirintos|labirinto]]
			- os [[Sensores de Entrada|sensores de entrada]] e os [[Sensores de Saída|sensores de saída]] funcionam em uníssono e as suas leituras são apresentadas em conjunto na forma de [[Mensagens de Movimento|mensagens de movimento]]

- exemplo de mensagem de movimento:

	 {Player:10, Marsami:40, RoomOrigin:3, RoomDestiny: 5, Status:1}

	- esta mensagem notifica o [[Jogadores|jogador]] #10 que o [[Marsamis|marsami]] #40 se movimentou da [[Salas|sala]] #3 para a sala #5
	- o estado (status) = 1 indica que não houve incidentes durante a [[Sensores de Movimento|leitura / travessia]] e é o estado normal a ser indicado nas mensagens
	- então que outros estados há e o que é que significam? [[Perguntas para a Próxima Reunião com o Docente]] (ver [[Status]])
	- caso a mensagem indique a sala #0 como sala de origem e outro valor qualquer para a sala de destino, esta mensagem pretende comunicar que o marsami foi [[introduzido no labirinto aquando da emissão da mensagem
	- caso a mensagem indique ambas as salas (sala de origem e sala de destino) como sala #0, a mensagem pretende comunicar que o marsami em questão não tem caminhos disponíveis para se movimentar e por isso permanece na mesma sala, ainda que não tenha atingido o [[Exaustão|estado de exaustão]]
