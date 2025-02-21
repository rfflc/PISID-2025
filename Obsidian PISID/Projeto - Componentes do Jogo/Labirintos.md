ver:
	[[Atuadores]]
	[[Corredores]]
	[[Jogadores]]
	[[Marsamis]]
	[[Portas]]
	[[Regras do Jogo]]
	[[Salas]]
	[[Sensores]]
	[[Sensores de Movimento]]
	[[Sensores de Entrada]]
	[[Sensores de Saída]]
	[[Sensores de Ruído]]

- cada [[Jogadores|jogador]] tem um labirinto individual atribuído e apenas interage com o seu labirinto
- neste labirinto circulam [[Marsamis|marsamis]] cujos movimentos são a [[Regras do Jogo|mecânica central do jogo]]
- os labirintos são compostos por [[Salas|salas]] unidas por [[Corredores|corredores]]
	- os corredores têm uma direção de passagem obrigatória
	- na junção dos dois existem [[Portas|portas]] que podem ser [[Atuadores|abertas e fechadas pelos jogadores]] de forma a limitar os [[Mensagens de Movimento|movimentos dos marsamis]]
		- nestas portas existem [[Sensores de Movimento|sensores de movimento]] que registam quando um marsami [[Sensores de Entrada|entra]] ou [[Sensores de Saída|sai]] de uma sala
- cada labirinto tem também um [[Sensores de Ruído|sensor de ruído]] que deteta o nível de [[Ruído|ruído]]
	- caso o nível de ruído exceda um [[Condições de Final de Jogo|limite predefinido]], [[Regras do Jogo|a ronda termina para o jogador]] (termina mesmo? e só a ronda ou o jogo inteiro? [[Perguntas para a Próxima Reunião com o Docente]])
- "no início, a [[Configuração do Labirinto|planta do labirinto]] é igual para todos" - isto refere-se a como a dinâmica de cada labirinto individual pode mudar por causa de portas fechadas ou há alguma forma de alterar a configuração dos labirintos / mudam a cada [[Largadas|ronda / largada]]? [[Perguntas para a Próxima Reunião com o Docente]] (confirmar)
	- as plantas divergem umas das outras apenas nas portas abertas e fechadas pelos jogadores (ou pelos sistemas automáticos), ergo, a planta não varia (pelo menos durante de cada largada)
