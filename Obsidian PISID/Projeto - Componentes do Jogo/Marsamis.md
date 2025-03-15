ver:
	[[Atuadores]]
	[[Condições de Final de Jogo]]
	[[Corredores]]
	[[Exaustão]]
	[[Labirintos]]
	[[Largadas]]
	[[Marsami (espécie)]]
	[[Mensagens de Movimento]]
	[[Portas]]
	[[Regras do Jogo]]
	[[Ruído]]
	[[Salas]]
	[[Sensores]]
	[[Sensores de Movimento]]
	[[Sensores de Entrada]]
	[[Sensores de Saída]]
	[[Sensores de Ruído]]

(singular: marsami)

- animais utilizados durante o [[Regras do Jogo|jogo]]

- os marsamis são soltos por [[Largadas|largadas]] nos diferentes [[Labirintos|labirintos]] (um labirinto por [[Jogadores|jogador]]) para que percorram as diferentes [[Salas|salas]]
	- as salas são ligadas por [[Corredores|corredores]] mas os marsamis não permanecem nos corredores

- existem dois tipos identificados pelo jogo:
	- odds (odd)
	- evens (even)
	- estes dois tipos não diferem em nada a não ser na nomenclatura

- durante o jogo, os [[Jogadores|jogadores]] podem [[Pontuação|marcar pontos]] ao ativar o [[Gatilho|gatilho]] quando o número de odds e evens é igual numa determinada sala sob penalização de perda de pontos caso errem no timing da ativação

- os marsamis deslocam-se entre as [[Atuadores|salas disponíveis]] até atingirem um estado de [[Exaustão|exaustão]]
	- as salas disponíveis são limitadas pela orientação dos corredores (que têm um sentido de deslocação obrigatório) e por [[Portas|portas fechadas]]
		- quando isto acontece, o marsami continua a ter mensagens de movimento associadas a ser emitidas, no entanto estas listam a origem e o destino como [[Sala 0|sala 0]]
	- o estado de exaustão é um limite artificialmente simulado no total de movimentos que cada marsami faz dentro de uma determinada ronda // largada
		- uma vez que o estado é atingido, o marsami pára de se movimentar e as mensagens de movimento passam a emitir o status '2'