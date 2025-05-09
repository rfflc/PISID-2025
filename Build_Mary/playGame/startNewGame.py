import paho.mqtt.client as mqtt
import subprocess
import mysql.connector
import time
import sys
import os
from dotenv import load_dotenv

load_dotenv()

DB_MAZE_CONFIG = {
    'host': os.getenv('DB_CLOUD_HOST'),
    'port': int(os.getenv('DB_CLOUD_PORT', 3306)),
    'user': os.getenv('DB_CLOUD_USER'),
    'password': os.getenv('DB_CLOUD_PASSWORD'),
    'database': os.getenv('DB_CLOUD_NAME')
}

DB_PISID_CONFIG = {
    'host': os.getenv('DB_LOCAL_HOST'),
    'port': int(os.getenv('DB_LOCAL_PORT', 3306)),
    'user': os.getenv('DB_LOCAL_USER'),
    'password': os.getenv('DB_LOCAL_PASSWORD'),
    'database': os.getenv('DB_LOCAL_NAME')
}

def get_setupmaze(iDJogo):
    try:
        print("A conectar à DB e obter cópia do mazesetup....")
        maze_conn = mysql.connector.connect(**DB_MAZE_CONFIG)
        pisid_conn = mysql.connector.connect(**DB_PISID_CONFIG)

        maze_cursor = maze_conn.cursor(dictionary=True)
        pisid_cursor = pisid_conn.cursor()

        maze_cursor.execute("SELECT * FROM setupmaze LIMIT 1")
        dados = maze_cursor.fetchone()

        if not dados:
            print("Nenhum dado encontrado na db maze.")
            return

        campos = ['normalnoise', 'numberrooms', 'numberplayers', 'frozentime',
                  'delaytime', 'timemarsamilive', 'noisevartoleration', 'step',
                  'minutesstep', 'minutessilence', 'randomsound', 'randommove']

        placeholders = ', '.join(['%s'] * (len(campos) + 1))  # +1 para iDJogo
        campos_sql = ', '.join(campos + ['iDJogo'])

        valores = [dados[c] for c in campos]
        valores.append(iDJogo)

        insert_query = f"INSERT INTO setupmaze ({campos_sql}) VALUES ({placeholders})"
        pisid_cursor.execute(insert_query, valores)
        pisid_conn.commit()

        print("Dados inseridos na db pisid com sucesso.")

    except Error as e:
        print(f"Erro ao copiar dados: {e}")
    finally:
        if maze_conn.is_connected():
            maze_cursor.close()
            maze_conn.close()
        if pisid_conn.is_connected():
            pisid_cursor.close()
            pisid_conn.close()

def get_corridors(iDJogo):
    try:
        print("A conectar à DB e obter cópia do mazesetup....")
        maze_conn = mysql.connector.connect(**DB_MAZE_CONFIG)
        pisid_conn = mysql.connector.connect(**DB_PISID_CONFIG)

        maze_cursor = maze_conn.cursor(dictionary=True)
        pisid_cursor = pisid_conn.cursor()

        maze_cursor.execute("SELECT * FROM corridor")
        dados = maze_cursor.fetchall()
        print(dados)
        if not dados:
            print("Nenhum dado encontrado na db maze.")
            return

        campos = ['Distance', 'Rooma', 'Roomb']

        placeholders = ', '.join(['%s'] * (len(campos) + 1))  # +1 para iDJogo
        campos_sql = ', '.join(campos + ['iDJogo'])

        valores = [dados[c] for c in campos]
        print(valores)
        valores.append(iDJogo)

        #insert_query = f"INSERT INTO setupmaze ({campos_sql}) VALUES ({placeholders})"
        #pisid_cursor.execute(insert_query, valores)
        #pisid_conn.commit()

        print("Dados inseridos na db pisid com sucesso.")

    except Error as e:
        print(f"Erro ao copiar dados: {e}")
    finally:
        if maze_conn.is_connected():
            maze_cursor.close()
            maze_conn.close()
        if pisid_conn.is_connected():
            pisid_cursor.close()
            pisid_conn.close()

# FUNÇÃO PRINCIPAL
def main():
    load_dotenv()
    print(DB_MAZE_CONFIG)
    #get_setupmaze(1)
    get_corridors(1)



if __name__ == "__main__":
    main()
