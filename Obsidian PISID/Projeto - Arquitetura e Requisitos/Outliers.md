ver:
	[[Alertas de Ruído]]  
	[[Arquitetura]]  
	[[Java]]  
	[[Jogadores]]  
	[[Marsamis]]  
	[[Mensagens de Movimento]]  
	[[Migração de MongoDB para SQL]]  
	[[MQTT]]  
	[[MySQL]]  
	[[Python]]  
	[[Ruído]]  
	[[Sala 0]]  
	[[Salas]]  
	[[Sensores]]  
	[[Sensores de Entrada]]  
	[[Sensores de Movimento]]  
	[[Sensores de Ruído]]  
	[[Sensores de Saída]]  
	[[Servidor Remoto]]  
	[[SQL]]  
	[[Status]]  
	[[Tabelas]]  
	[[Tabelas Recomendadas]]  

Potenciais outliers para mensagens (no geral):
- [ ] formato não reconhecido

Potenciais outliers para mensagens de movimento:
- [ ] player errado
- [ ] sala impossível
- [ ] marsami impossível
- [ ] status impossível

Potenciais outliers para mensagens de ruído:
- [ ] valor negativo
- [ ] labirinto / player errado

Outliers que terão de ser tratados na camada 2 ([[Migração de MongoDB para SQL|camada de migração]]):
- player errado
- marsami com ID superior à quantidade de marsamis no jogo
- sala com ID superior à quantidade de salas no labirinto
- corredor impossível
- corredor fechado
- 