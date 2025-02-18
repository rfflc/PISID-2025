ver:
	[[MongoDB]]

MongoDB Commands

...........................................................................................................

To start mongodb/brew/mongodb-community now and restart at login :

	brew services start mongodb/brew/mongodb-community

To stop : (you can kill these manually via settings also)

	brew services stop mongodb/brew/mongodb-community

You can also run the following command to check where brew has installed these files and directories :

	brew --prefix

Ver versão MongoDB instalada (atenção ao mongod) :

	mongod --version

Update MongoDB Tools :

	brew upgrade mongodb-database-tools

...........................................................................................................

For MongoShell // Within MongoShell :

Launch MongoDB shell : (command queue should be 'test>' after this)

	mongosh

Exit MongoDB shell : (while the command queue is 'test>' , takes you out of mongoshell)

	exit

Clear screen in mongoshell :

	cls

show all databases : (empty databases won't show up)

	show dbs
