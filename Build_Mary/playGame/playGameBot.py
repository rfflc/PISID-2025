import subprocess
import mysql.connector
import paho.mqtt.client as mqtt
import time
import os
import argparse
import random
from mysql.connector import Error
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

#CRIA UM CLIENT MQTT E PUBLICAR
def mqtt_publish(client, topic, message):
    client.publish(topic, message)

def setup_mqtt():
    client = mqtt.Client()
    client.connect("broker.emqx.io", 1883)
    return client

#EXECUTA O JOGO
def start_game_executable(path):
    return subprocess.Popen([path], creationflags=subprocess.CREATE_NEW_CONSOLE)

#ESTABLECE E MANTÉM UMA CONEXÂO À DB LOCAL
def get_db_connection(config=DB_PISID_CONFIG):
    while True:
        try:
            conn = mysql.connector.connect(**config)
            if conn.is_connected():
                print(f"Conectado à base de dados: {config['host']}")
                return conn
        except Error as e:
            print(f"Erro ao conectar à base de dados. Tentando novamente... {e}")
            time.sleep(2)

#COPIA O SETUPMAZE PARA A DB LOCAL
def get_setupmaze(IDJogo):
    try:
        print("A conectar à DB e obter cópia do setupmaze...")
        maze_conn = mysql.connector.connect(**DB_MAZE_CONFIG)
        pisid_conn = mysql.connector.connect(**DB_PISID_CONFIG)

        maze_cursor = maze_conn.cursor(dictionary=True)
        pisid_cursor = pisid_conn.cursor()

        maze_cursor.execute("SELECT * FROM setupmaze LIMIT 1")
        dados = maze_cursor.fetchone()

        if not dados:
            print("Nenhum dado encontrado na db maze.")
            return None, None

        campos = ['normalnoise','frozentime','noisevartoleration']

        placeholders = ', '.join(['%s'] * (len(campos) + 1))
        campos_sql = ', '.join(campos + ['idjogo'])

        valores = [dados[c] for c in campos]
        valores.append(IDJogo)

        insert_query = f"INSERT INTO setupmaze ({campos_sql}) VALUES ({placeholders})"
        pisid_cursor.execute(insert_query, valores)
        pisid_conn.commit()

        print("setupmaze inserido com sucesso na DB local.")
        return dados['normalnoise'], dados['noisevartoleration']

    except mysql.connector.Error as e:
        print(f"Erro ao copiar setupmaze: {e}")
        return None, None
    finally:
        if maze_conn.is_connected():
            maze_cursor.close()
            maze_conn.close()
        if pisid_conn.is_connected():
            pisid_cursor.close()
            pisid_conn.close()

def get_corridors(IDJogo):
    try:
        print("A conectar à DB e obter cópia dos corredores...")
        maze_conn = mysql.connector.connect(**DB_MAZE_CONFIG)
        pisid_conn = mysql.connector.connect(**DB_PISID_CONFIG)

        maze_cursor = maze_conn.cursor(dictionary=True)
        pisid_cursor = pisid_conn.cursor()

        maze_cursor.execute("SELECT * FROM corridor")
        dados = maze_cursor.fetchall()

        if not dados:
            print("Nenhum dado encontrado na db maze.")
            return

        insert_query = """
            INSERT INTO corridor (id_corredor, Distance, salaA, salaB, idjogo, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        for row in dados:
            pisid_cursor.execute(insert_query, (
                row['ID'],
                row['Rooma'],
                row['Roomb'],
                'aberto',
                IDJogo
            ))

        pisid_conn.commit()
        print(f"{len(dados)} corredores inseridos com sucesso na DB local.")

    except mysql.connector.Error as err:
        print(f"Erro ao copiar corredores: {err}")
    finally:
        if maze_conn.is_connected():
            maze_cursor.close()
            maze_conn.close()
        if pisid_conn.is_connected():
            pisid_cursor.close()
            pisid_conn.close()

#LOOP QUE MONITORIZA O JOGO E CORRE A LÓGICA
last_level = 1

def monitor_game(IDJogo, groupNumber, exe_process, mqtt_client, normalnoise, noisevartoleration):
    conn = get_db_connection(DB_PISID_CONFIG)
    cursor = conn.cursor(dictionary=True)
    doors_closed = False

    try:
        while exe_process.poll() is None:
            doors_closed = check_sound_and_rooms(cursor, IDJogo, mqtt_client, normalnoise, noisevartoleration, doors_closed)
            check_room_balance_and_score(cursor, groupNumber, mqtt_client)
            time.sleep(2)
    except Exception as e:
        print(f"Erro durante o jogo: {e}")
    finally:
        mark_game_as_terminated(conn, IDJogo)
        cursor.close()
        conn.close()

#LOGICA DE JOGO
def check_sound_and_rooms(cursor, IDJogo, groupNumber,mqtt_client, normalnoise, noisevartoleration, doors_closed):
    global last_level

    cursor.execute("SELECT soundlevel FROM sound WHERE idjogo = %s ORDER BY id_sound DESC LIMIT 1", (IDJogo,))
    sound = cursor.fetchone()

    if not sound:
        return doors_closed

    current = sound['soundlevel']
    hour = sound['hour']
    level_1_max = normalnoise + (1/3 * noisevartoleration)
    level_2_max = normalnoise + (2/3 * noisevartoleration)

    if current <= level_1_max:
        level = 1
    elif current <= level_2_max:
        level = 2
    else:
        level = 3

    print(f"[Sound] Current: {current:.2f}, Level: {level}")

    if level == 1 and last_level != 1:
        mqtt_publish(mqtt_client, "pisid_mazeact", str({"Type": "OpenAllDoor", "Player": IDJogo}))
        cursor.execute("UPDATE corridor SET status = 'open' WHERE idjogo = %s", (IDJogo,))
        cursor.connection.commit()
        last_level = 1
        return False

    if level == 2 and last_level != 2:
        inserir_mensagem(cursor, IDJogo, current, "alerta_ruido", mensagem="Nível de som elevado", hora=hour)
        cursor.execute("SELECT id FROM corridor WHERE idjogo = %s AND status = 'aberto'", (IDJogo,))
        open_doors = cursor.fetchall()
        half_to_close = random.sample(open_doors, k=len(open_doors)//2)
        for row in half_to_close:
            message = "{Type: CloseDoor, Player:" + str(groupNumber) +  ", RoomOrigin: " + str(row['salaa']) + ", RoomDestiny: " + str(row['salab']) + "}"
            mqtt_publish(mqtt_client, "pisid_mazeact", message)
            cursor.execute("UPDATE corridor SET status = 'closed' WHERE id_corredor = %s", (row['id_corredor'],))
        cursor.connection.commit()
        print(f"[MQTT] Closed {len(half_to_close)} random doors (Level 2)")
        last_level = 2
        return True

    if level == 3 and last_level != 3:
        message = '{Type: CloseAllDoor, Player:' + str(groupNumber) + '}'
        mqtt_publish(mqtt_client, "pisid_mazeact", message)
        cursor.execute("UPDATE corridor SET status = 'closed' WHERE idjogo = %s", (IDJogo,))
        cursor.connection.commit()
        last_level = 3
        print(f"Sound level too high at {current}")
        inserir_mensagem(cursor, IDJogo, current, "alerta_ruido", mensagem="Nível de som muito elevado", hora=hour)
        time.sleep(15)
        message = '{Type: OpenAllDoor, Player:' + str(groupNumber) + '}'
        cursor.execute("UPDATE corridor SET status = 'open' WHERE idjogo = %s", (IDJogo,))
        cursor.connection.commit()
        return True

    return doors_closed

def check_room_balance_and_score(cursor, IDJogo, groupNumber, mqtt_client):
    cursor.execute("SELECT sala, even, odd FROM ocupacaolabirinto")
    for row in cursor.fetchall():
        room = row['sala']
        even = row['even']
        odd = row['odd']

        if even > 0 and even == odd:
            message = '{Type: Score, Player:' + str(groupNumber) + ', Room: ' + str(room) +'}'
            mqtt_publish(mqtt_client, "pisid_mazeact", str(message))
            str = f"Gatilho accionado na sala {room}"
            inserir_mensagem(cursor, IDJogo, 0, "gatilho", mensagem=str,sala=room, hora=hour)
            print(f"[MQTT] Score triggered for Room {room}")

def inserir_mensagem(cursor, idjogo, leitura, tipo, mensagem, sala=None, sensor=None, hora=None):
    if tipo not in {'alerta_ruido', 'gatilho', 'erro'}:
        raise ValueError("Tipo inválido de mensagem.")

    sala = 0 if sala is None else sala
    sensor = 0 if sensor is None else sensor

    if hora:
        cursor.execute(
            """
            INSERT INTO mensagens (idjogo, leitura, sala, sensor, tipo, mensagem, hora)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (idjogo, leitura, sala, sensor, tipo, mensagem, hora)
        )
    else:
        cursor.execute(
            """
            INSERT INTO mensagens (idjogo, leitura, sala, sensor, tipo, mensagem)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (idjogo, leitura, sala, sensor, tipo, mensagem)
        )
    cursor.connection.commit()


def mark_game_as_terminated(conn, IDJogo):
    cursor = conn.cursor()
    cursor.execute("UPDATE jogo SET estado = 'terminado' WHERE idjogo = %s", (IDJogo,))
    conn.commit()
    cursor.close()
    print("Jogo marcado como terminado.")

#Main
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("IDJogo", type=int, help="ID do jogo")
    parser.add_argument("groupNumber", type=int, help="Número do grupo")
    args = parser.parse_args()

    IDJogo = args.IDJogo
    groupNumber = args.groupNumber
    exe_path = "C:\\caminho\\para\\o\\jogo.exe"

    mqtt_client = setup_mqtt()
    mqtt_publish(mqtt_client, "layer1_layer2_22", f"grupo:{groupNumber}")

    get_corridors(IDJogo)
    normalnoise, noisevartoleration = get_setupmaze(IDJogo)

    if normalnoise is None or noisevartoleration is None:
        print("Erro ao carregar dados de setupmaze. Encerrando...")
        return

    process = start_game_executable(exe_path)
    monitor_game(IDJogo, groupNumber,process, mqtt_client, normalnoise, noisevartoleration)

if __name__ == "__main__":
    main()