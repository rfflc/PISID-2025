ver:
	[[Atuadores]]
	[[Condições de Final de Jogo]]
	[[Labirintos]]
	[[Largadas]]
	[[Marsamis]]
	[[Portas]]
	[[Pontuação]]
	[[Regras do Jogo]]
	[[Sensores]]
	[[Sensores de Ruído]]

- o nível de ruído é uma [[Regras do Jogo|mecânica do jogo]], se o valor da leitura atinge um limite estipulado, os sistemas automáticos [[Condições de Final de Jogo|suspendem / terminam a ronda / jogo]] ao [[Jogadores|jogador]]
- o nível de ruído é calculado artificialmente (simulado) pelo script de [[Python]] do [[Sensores de Ruído|sensor de ruído]] em função do número de [[Sensores de Movimento|movimentos detetados]] dentro do [[Labirintos|labirinto]]
	- os movimentos também são simulados
	- a função exata é desconhecida mas é "proporcional"
		- o valor médio é 18 segundo o enunciado e 19 experimentalmente
	- naturalmente, abrir portas aumenta o número de movimentos o que aumenta o nível de ruído e fechar portas reduz o número de movimentos o que reduz o ruído
		- a operação das portas em si não afeta o nível de ruído
	- então, ao abrir as portas todas ou ao não começar imediatamente a fechar portas corre-se o risco de se ultrapassar logo o limite de ruído
	- o valor de ruído é tão dinâmico / volátil quanto quisermos dado que depende do intervalo entre medições e quaisquer sistemas de deteção de outliers nós empreguemos
