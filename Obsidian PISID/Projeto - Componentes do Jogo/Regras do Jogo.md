ver: 
	[[Arquitetura]]
	[[Atuadores]]
	[[Condições de Final de Jogo]]
	[[Configuração do Labirinto]]
	[[Jogadores]]
	[[Labirintos]]
	[[Marsamis]]
	[[Requisitos]]

- o jogo envolve vários [[Jogadores|jogadores]]
- cada jogador tem um [[Labirintos|labirinto]] associado
- os labirintos são estanques, ou seja, as ações tomadas durante um jogo não afetam os restantes jogos, concorrentes ou não
- o jogo decorre por [[Largadas|largadas]] nas quais são libertados grupos de [[Marsamis|marsamis]] em cada labirinto
	- cada largada / ronda começa com todas as [[Portas|portas]] do labirinto abertas
- uma (1) única ronda por jogo
- uma (1) única largada por jogo
- as [[Salas|salas]] nas quais os marsamis são inicialmente colocados variam de jogo para jogo
- as salas não variam de labirinto / jogador para jogador, a topologia é sempre a mesma (excluindo a dinâmica de portas [[Atuadores|abertas e fechadas]])
- os marsamis, no momento em que são colocados / soltos nos labirintos, correm até à exaustão, podendo trocar de sala até ao momento em que atingem a mencionada exaustão
	- (os marsamis são simulados no mesmo script que simula os sensores de movimento)
	- a troca de salas é feita dentro dos caminhos possíveis
		- tendo em conta que os corredores que ligam as salas têm direções de circulação obrigatória e que as portas que os ligam podem ser fechadas pelos jogadores, é possível que um marsami seja impedido de mudar de sala
			- isto é contemplado no sistema de [[Mensagens de Movimento|mensagens de movimento]]
- há dois tipos de marsamis soltos durante cada largada:
	- odds (odd)
	- evens (even) 
- cada jogador tem acesso a um [[Gatilho|gatilho]] por sala que deve pressionar quando estima que o número de odds e evens na mesma é exatamente igual
	- há um gatilho por sala
	- ao pressionar o gatilho, o jogador ganha [[Pontuação|um ponto caso a igualdade ainda se mantenha ou perde meio ponto caso se tenha alterado]]
		- os jogadores iniciam os jogo com zero pontos cada
			- é possível acumular uma pontuação negativa
- em adição ao gatilho, cada jogador tem acesso a [[Atuadores|atuadores]] que abrem e fecham as portas entre os corredores e as salas
	- cada jogador controla apenas as portas no seu próprio labirinto
	- o jogador tem quatro opções:
		- abrir uma porta individual (porta específica à escolha)
		- fechar uma porta individual (porta específica à escolha)
		- abrir todas as portas
		- fechar todas as portas
	- este controlo é suspendido quando a ronda termina ou o [[Ruído|limite de ruído]] é atingido
		- o ruído é simulado (no script Python do [[Sensores de Ruído|sensor de ruído]] )
		- no caso do limite de ruído ser ultrapassado as portas são automaticamente fechadas, efetivamente terminando / bloqueando a ronda para o jogador em causa
