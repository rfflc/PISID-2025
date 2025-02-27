ver: 
	[[Arquitetura]]
	[[Java]]
	[[Python]]
	[[MQTT]]
	[[MongoDB]]
	[[Migração de MongoDB para SQL]]
	[[PC2]]
	[[Servidor Remoto]]

- máquina que vai representar o servidor de [[MongoDB]] (e as suas réplicas)
- na prática será um dos computadores do grupo a correr a BD de MongoDB
- recebe as deteções dos [[Sensores|sensores]] simulados no [[Servidor Remoto|servidor remoto]]
- [[Migração de MongoDB para SQL|os dados depois seguem]] para a BD em [[SQL]] no [[PC2]]
- a comunicação (in e out) com esta máquina é feita por [[Java]] ou [[Python]] e pode ou não utilizar [[MQTT]]
