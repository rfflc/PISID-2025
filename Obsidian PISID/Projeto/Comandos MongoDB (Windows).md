
Here are the MongoDB commands adapted for Windows:

### Starting and Stopping MongoDB Service

To start MongoDB service on Windows:

```bash
net start MongoDB
```

To stop MongoDB service on Windows:

```bash
net stop MongoDB
```

### Checking MongoDB Version

To check the installed MongoDB version on Windows:

```bash
mongod --version
```

### Updating MongoDB Tools

To update MongoDB tools on Windows, you would typically download the latest version from the [MongoDB Download Center](https://www.mongodb.com/try/download/database-tools) and install it manually.

### MongoDB Shell (mongosh)

To launch MongoDB shell on Windows:

```bash
mongosh
```

To exit MongoDB shell:

```bash
exit
```

To clear the screen in MongoDB shell on Windows:

```bash
cls
```

### Show All Databases

To show all databases in MongoDB shell:

```bash
show dbs
```

### Additional Commands

To check where MongoDB is installed on Windows, you can look at the installation path during setup or check the environment variables.

To check the MongoDB service status on Windows:

```bash
sc query MongoDB
```

These commands should help you manage MongoDB on a Windows system.