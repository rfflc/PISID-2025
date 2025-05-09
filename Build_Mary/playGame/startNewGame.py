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
        print("A conectar à DB e obter cópia dos corredores....")
        #abrir a conexão com as db's (local e cloud)
        maze_conn = mysql.connector.connect(**DB_MAZE_CONFIG)
        pisid_conn = mysql.connector.connect(**DB_PISID_CONFIG)

        maze_cursor = maze_conn.cursor(dictionary=True)
        pisid_cursor = pisid_conn.cursor()

        #Fetch todos as linhas presentes na tabela corridor do servidor cloud
        maze_cursor.execute("SELECT * FROM corridor")
        dados = maze_cursor.fetchall()
        print(dados)
        if not dados:
            print("Nenhum dado encontrado na db maze.")
            return

        # Inserir na bd local
        for row in dados:
            distance = row['Distance']
            room_a = row['Rooma']
            room_b = row['Roomb']

            insert_query = """
                           INSERT INTO corridor (Distance, salaA, salaB, iDJogo)
                           VALUES (%s, %s, %s, %s) \
                           """
            pisid_cursor.execute(insert_query, (distance, room_a, room_b, iDJogo))

            pisid_conn.commit()
            print(f"{len(dados)} corredores inseridos com sucesso na base de dados local.")

    except mysql.connector.Error as err:
        print(f"Erro ao aceder às bases de dados: {err}")
    finally:
        maze_cursor.close()
        pisid_cursor.close()
        maze_conn.close()
        pisid_conn.close()

#funções para iniciar e controlar o jogo
def start_game_executable(path, groupNumber):
    return subprocess.Popen([path, str(groupNumber)],
                            creationflags=subprocess.CREATE_NEW_CONSOLE)
def monitor_game(groupNumber, exe_process, mqtt_client):
    try:
        while exe_process.poll() is None:
            #check_sound_and_rooms(iDJogo, mqtt_client)
            time.sleep(2)  # adjust as needed
    except Exception as e:
        print(f"Erro durante o jogo: {e}")
    finally:
        #mark_game_as_terminated(iDJogo)
        print("Jogo terminado")


#LÓGICA DE JOGO
def check_room_balance_and_score(iDJogo, mqtt_client):
    conn = mysql.connector.connect(**DB_PISID_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT sala, NumeroMarsamisEven, NumeroMarsamisOdd
        FROM ocupaçãolabirinto
    """)

    for row in cursor.fetchall():
        room = row['sala']
        even = row['NumeroMarsamisEven']
        odd = row['NumeroMarsamisOdd']

        if even > 0 and even == odd:
            message = {
                "Type": "Score",
                "Player": iDJogo,       # assuming player ID == iDJogo; adjust if needed
                "Room": room
            }
            mqtt_client.publish("pisid_mazeact", str(message))
            print(f"Score triggered for Room {room}: {message}")

    cursor.close()
    conn.close()


# FUNÇÃO PRINCIPAL
def main():
    load_dotenv()
    print(DB_MAZE_CONFIG)
    #get_setupmaze(1)
    get_corridors(1)



if __name__ == "__main__":
    main()
