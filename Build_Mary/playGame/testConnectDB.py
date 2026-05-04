import mysql.connector
from mysql.connector import Error

DB_MAZE_CONFIG = {
    'host': '194.210.86.10',
    'port': 3306,
    'user': 'aluno',
    'password': 'aluno',
    'database': 'maze'
}

DB_PISID_CONFIG = {
    'host': '12.0.0.1',
    'port': 3306,
    'user': 'usuario_pisid',
    'password': 'senha_pisid',
    'database': 'pisid'
}

maze_conn = mysql.connector.connect(**DB_MAZE_CONFIG)
maze_cursor = maze_conn.cursor(dictionary=True)
maze_cursor.execute("SELECT * FROM setupmaze LIMIT 1")
dados = maze_cursor.fetchone()

print(dados)