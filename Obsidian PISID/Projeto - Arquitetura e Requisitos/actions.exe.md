ver:
	[[Arquitetura]]  
	[[Atuadores]]  
	[[Jogadores]]  
	[[Jogadores Android]]  
	[[Jogadores Web]]  
	[[MySQL]]  
	[[Stored Procedures]]  
	[[PHP]]  
	[[Python]]  
	[[Servidor Remoto]]  
	[[MQTT]]  
	[[PC2]]  
	[[Portas]]  
	[[HTML]]  
	[[SQL]]

- ficheiro executável (.exe) que abre um canal de comunicação com o [[Servidor Remoto|servidor remoto]] para que informação sobre as [[Portas|portas]] que são [[Atuadores|abertas e fechadas]] possa ser enviada para que o script [[Python]] que simula os [[Sensores de Movimento|sensores de movimento]] evite movimentos que seriam impossíveis dado o fecho das portas

- deve ser lançado antes do outro executável, [[game.exe]] para que o canal de comunicação esteja aberto quando o jogo é iniciado