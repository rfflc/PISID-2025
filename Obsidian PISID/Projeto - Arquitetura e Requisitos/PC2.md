ver:
	[[Arquitetura]]
	[[Java?]]
	[[Python]]
	[[MQTT]]
	[[Migração de MongoDB para SQL]]
	[[Projeto - Tecnologias/SQL]]
	[[PC1]]
	[[Servidor Remoto]]

- máquina que vai representar o servidor de [[SQL]] (em [[MySQL]])
- na prática será um dos computadores do grupo a correr a BD de SQL
- recebe os [[Migração de MongoDB para SQL|dados tratados]] vindos da BD em [[MongoDB]] no [[PC1]] e do [[Servidor Remoto]] (supostamente há um [[MySQL]] a correr no servidor mas convém esclarecer em que capacidade e com que papel [[Perguntas para a Próxima Reunião com o Docente]])
- [[Migração de MongoDB para SQL|os dados depois seguem]] para os [[Jogadores|jogadores]] e para o [[Servidor Remoto|servidor remoto]]
- a comunicação (in e out) com esta máquina é feita por [[Java?]] ou [[Python]] e pode ou não utilizar [[MQTT]], por [[HTML]] que pode ou não utilizar [[PHP]]
