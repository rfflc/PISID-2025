ver:
	[[Condições de Final de Jogo]]
	[[Sensores de Ruído]]

- o nível de ruído é calculado artificialmente (simulado) pelo script de Python do [[Sensores de Ruído|sensor de ruído]] em função do número de [[Sensores de Movimento|movimentos detetados]] dentro do [[Labirinto|labirinto]]
	- os movimentos também são simulados
	- a função exata é desconhecida (ver código dado) ou [[Perguntas para a Próxima Reunião com o Docente]] mas é proporcional
	- naturalmente, abrir portas aumenta o número de movimentos o que aumenta o nível de ruído e fechar portas reduz o número de movimentos o que reduz o ruído
	- então, ao abrir as portas todas ou ao não começar imediatamente a fechar portas corre-se o risco de se ultrapassar logo o limite de ruído [[Perguntas para a Próxima Reunião com o Docente]]
	- quão dinâmico / volátil é o valor de ruído [[Perguntas para a Próxima Reunião com o Docente]]