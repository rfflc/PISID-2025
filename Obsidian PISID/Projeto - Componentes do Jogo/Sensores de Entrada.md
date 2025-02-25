ver:
	[[Corredores]]
	[[Labirintos]]
	[[Python]]
	[[Regras do Jogo]]
	[[Salas]]
	[[Sensores]]
	[[Sensores de Movimento]]
	[[Sensores de Saída]]

- sensores simulados por [[Python|scripts de Python]] que correm no [[Servidor Remoto|servidor remoto]]
- - detetam quando um [[Marsamis|marsami]] entra numa sala (i.e., passa de um corredor para uma sala)
- estes sensores, em conjunto com os [[Sensores de Saída|sensores de saída]], simulam os movimentos de marsamis dentro dos [[Labirintos|labirintos]]
	- os movimentos são apresentados como [[Mensagens de Movimento|mensagens de movimento]] à base de dados não-relacional no [[PC1]]
