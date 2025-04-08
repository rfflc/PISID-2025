ver:
	[[Condições de Final de Jogo]]
	[[Corredores]]
	[[Jogadores]]
	[[Labirintos]]
	[[Marsamis]]
	[[Portas]]
	[[Regras do Jogo]]
	[[Salas]]
	[[Sensores de Movimento]]

- abrem e fecham [[Portas|portas]]
- são operados pelos [[Jogadores|jogadores]] durante o jogo e pelos sistemas automáticos associados à mecânica de [[Ruído|limites de ruído]]
- o jogador tem quatro opções:
	- abrir uma porta individual (porta específica à escolha)
	- fechar uma porta individual (porta específica à escolha)
	- abrir todas as portas
	- fechar todas as portas
	- as opções de abrir e fechar todas as portas não afeta os outros labirintos
- as portas estão posicionadas na ligação corredor-sala
	- dado que os movimentos pelos [[Corredores|corredores]] e o acionar de portas são ambos considerados atómicos e perfeitos, não faz grande diferença
- a ativação do botão resulta numa emissão de sinal para o [[Servidor Remoto|servidor remoto]] para que este possa refletir as mudanças causadas pelo jogador na simulação dos [[Mensagens de Movimento|movimentos dos marsamis]]
	- esta informação será reflectida na BD do [[PC1]] e [[Migração de MongoDB para SQL|subsequentemente]] na BD do [[PC2]]
