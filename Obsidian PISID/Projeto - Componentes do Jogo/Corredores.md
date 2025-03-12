ver:
	[[Atuadores]]
	[[Labirintos]]
	[[Marsamis]]
	[[Portas]]
	[[Salas]]
	[[Sensores de Movimento]]

- nos [[Labirintos|labirintos]] onde decorre o [[Regras do Jogo|jogo]], [[Marsamis|marsamis]] percorrem as diferentes [[Salas|salas]] através de corredores
	- os corredores têm sentido de passagem obrigatório
	- entradas e saídas de corredores e salas são detetadas por [[Sensores de Movimento|sensores de movimento]]
		- existem [[Sensores de Entrada|sensores de entrada nas salas]] e [[Sensores de Saída|sensores de saída das salas]] (a nomenclatura é feita do ponto de vista das salas)
		- é garantido que uma passagem lida pelos sensores de movimento corresponda à passagem de um único marsami no sentido correto
- cada corredor une apenas duas salas
	- não há corredores-beco
	- há loops de dar voltas que passem por outras salas
	- não há loops que começam e acabam na mesma sala
	- vários corredores podem estar ligados à mesma sala
