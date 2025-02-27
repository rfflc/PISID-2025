ver: 
	[[Arquitetura]]
	[[Corredores]]
	[[Java]]
	[[Python]]
	[[MQTT]]
	[[Labirintos]]
	[[PC1]]
	[[PC2]]
	[[Regras do Jogo]]
	[[Ruído]]
	[[Salas]]
	[[Sensores]]
	[[Sensores de Movimento]]
	[[Sensores de Entrada]]
	[[Sensores de Saída]]
	[[Sensores de Ruído]]

- servidor fornecido e gerido pelos docentes da careira que incorpora:
	- [[Sensores|sensores cujos sinais / outputs são simulados]], isto inclui:
		- [[Sensores de Movimento|sensores de movimento]] que simulam os movimentos dos [[Marsamis|marsamis]] no [[Labirintos|labirinto]]
			- os [[Sensores de Entrada|sensores de entrada]] e os [[Sensores de Saída|sensores de saída]] funcionam em uníssono e as suas leituras são apresentadas em conjunto na forma de [[Mensagens de Movimento|mensagens de movimento]]
		- [[Sensores de Ruído|sensores de ruído]] que simulam o nível de ruído gerado pelos movimentos dos marsamis em cada labirinto
	- um servidor ou instância de [[MySQL]] que corresponde com a BD em [[MySQL]] no [[PC2]]
		- a capacidade na qual esta instância existe e interage com a BD de [[SQL]] é ainda desconhecida [[Perguntas para a Próxima Reunião com o Docente]]
- este servidor é esperado estar disponível através do Eduroam (internet do ISCTE e outros institutos de ensino superior associados com o programa) e através de uma VPN (Virtual Private Network) disponibilizada ad-hoc para acesso ao servidor remoto [[Perguntas para a Próxima Reunião com o Docente]] (criar página com instruções para ligar à VPN se houver uma [[Lista de Tarefas]])
