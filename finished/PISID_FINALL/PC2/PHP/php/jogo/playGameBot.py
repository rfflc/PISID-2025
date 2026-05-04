import subprocess
import mysql.connector
import paho.mqtt.client as mqtt
import time
import os
import argparse
import random
from mysql.connector import Error
from dotenv import load_dotenv
from decimal import Decimal
from datetime import datetime
import json

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
    return subprocess.Popen(path, creationflags=subprocess.CREATE_NEW_CONSOLE)

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
            INSERT INTO corridor (salaa, salab, status, idjogo)
            VALUES (%s, %s, %s, %s)
        """

        for row in dados:
            pisid_cursor.execute(insert_query, (
                row['Rooma'],
                row['Roomb'],
                'open',
                IDJogo
            ))

        for i in range(1,11):
            pisid_cursor.execute(insert_query, (
                0,
                i,
                'open',
                IDJogo
            ))
        insert_query_lab = """
                       INSERT INTO ocupacaolabirinto (sala, idjogo)
                       VALUES (%s, %s)"""
        for i in range(0,11):
            pisid_cursor.execute(insert_query_lab, (
                i,
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
    #conn = get_db_connection(DB_PISID_CONFIG)
    #cursor = conn.cursor(dictionary=True)
    doors_closed = False

    try:
        while exe_process.poll() is None:
            try:
                conn = get_db_connection(DB_PISID_CONFIG)
                cursor = conn.cursor(dictionary=True)

                try:
                    check_sound_and_rooms(cursor, conn, IDJogo, groupNumber, mqtt_client, normalnoise,
                                          noisevartoleration)
                    check_room_balance_and_score(cursor, conn, IDJogo, groupNumber, mqtt_client)
                    time.sleep(2)

                finally:
                    cursor.close()
                    conn.close()

            except KeyboardInterrupt:
                print("\n[INFO] Interrupção manual detectada (Ctrl+C).")
                mark_game_as_terminated(IDJogo, mqtt_client)
                break

            time.sleep(2)

    except Exception as e:
        print(f"[ERRO] Erro durante o jogo: {e}")

    finally:
        print("[INFO] Finalizando jogo...")
        try:
            mark_game_as_terminated(IDJogo, mqtt_client)
        except Exception as e:
            print(f"[WARN] Não foi possível marcar o jogo como terminado: {e}")

#LOGICA DE JOGO
def check_sound_and_rooms(cursor, conn, IDJogo, groupNumber,mqtt_client, normalnoise, noisevartoleration):
    global last_level
    print(IDJogo)
    cursor.execute("SELECT * FROM sound ORDER BY id_sound DESC LIMIT 1")
    sound = cursor.fetchone()
    print("[DEBUG] Resultado da query sound:", sound)

    if not sound:
        print("[Sound] Nenhum som encontrado ainda. A aguardar...")
        return False

    current = sound['soundlevel']
    hour = sound['hour']
    level_1_max = normalnoise + (Decimal('1') / Decimal('3') * noisevartoleration)
    level_2_max = normalnoise + (Decimal('2') / Decimal('3') * noisevartoleration)

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
        conn.commit()
        last_level = 1
        return False

    if level == 2 and last_level != 2:
        inserir_mensagem(cursor, conn,IDJogo, current, "alerta_ruido", mensagem="Nível de som elevado", hora=hour)
        cursor.execute("SELECT id_corredor, salaa, salab  FROM corridor WHERE idjogo = %s AND status = 'open'", (IDJogo,))
        open_doors = cursor.fetchall()
        half_to_close = random.sample(open_doors, k=len(open_doors)//2)
        for row in half_to_close:
            message = "{Type: CloseDoor, Player:" + str(groupNumber) +  ", RoomOrigin: " + str(row['salaa']) + ", RoomDestiny: " + str(row['salab']) + "}"
            mqtt_publish(mqtt_client, "pisid_mazeact", message)
            cursor.execute("UPDATE corridor SET status = 'closed' WHERE id_corredor = %s", (row['id_corredor'],))
        conn.commit()
        print(f"[MQTT] Closed {len(half_to_close)} random doors (Level 2)")
        last_level = 2
        return True

    if level == 3 and last_level != 3:
        message = '{Type: CloseAllDoor, Player:' + str(groupNumber) + '}'
        mqtt_publish(mqtt_client, "pisid_mazeact", message)
        cursor.execute("UPDATE corridor SET status = 'closed' WHERE idjogo = %s", (IDJogo,))
        conn.commit()
        last_level = 3
        print(f"Sound level too high at {current}")
        inserir_mensagem(cursor, conn, IDJogo, current, "alerta_ruido", mensagem="Nível de som muito elevado", hora=hour)
        time.sleep(15)
        message = '{Type: OpenAllDoor, Player:' + str(groupNumber) + '}'
        mqtt_publish(mqtt_client, "pisid_mazeact", message)
        cursor.execute("UPDATE corridor SET status = 'open' WHERE idjogo = %s", (IDJogo,))
        conn.commit()
        return True

    return False

def check_room_balance_and_score(cursor, conn, IDJogo, groupNumber, mqtt_client):
    cursor.execute("SELECT sala, even, odd, triggersused FROM ocupacaolabirinto")
    rows =cursor.fetchall()
    print("[DEBUG] Resultado da query ocupacaolabirinto:", rows)
    if not rows:
        print("[Occupancy] Nenhuma sala encontrada ainda. A aguardar...")
        return  # Volta ao loop e tenta de novo
    for row in rows:
        room = row['sala']
        even = row['even']
        odd = row['odd']
        triggers = row.get('triggersused', 0)

        if even > 0 and even == odd and triggers < 3:
            message = '{Type: Score, Player:' + str(groupNumber) + ', Room: ' + str(room) +'}'
            mqtt_publish(mqtt_client, "pisid_mazeact", str(message))
            str_tmp = f"Gatilho accionado na sala {room}"
            inserir_mensagem(cursor, conn, IDJogo, 0, "gatilho", mensagem=str_tmp,sala=room, hora=datetime.now())
            print(f"[MQTT] Score triggered for Room {room}")

            cursor.execute(
                "UPDATE ocupacaolabirinto SET triggersused = triggersused + 1 WHERE idjogo = %s AND sala = %s",
                (IDJogo, room)
            )
            conn.commit()

def inserir_mensagem(cursor, conn ,idjogo, leitura, tipo, mensagem, sala=None, sensor=None, hora=None):
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
    conn.commit()


def mark_game_as_terminated(IDJogo, mqtt_client):
    conn = get_db_connection(DB_PISID_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("UPDATE jogo SET estado = 'terminado', fim = NOW() WHERE idjogo = %s", (IDJogo,))
    conn.commit()
    cursor.close()
    mqtt_publish(mqtt_client, "pisid_keepalive_22", {"end" : "True"})
    print("Jogo marcado como terminado.")

#Main
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("IDJogo", type=int, help="ID do jogo")
    parser.add_argument("groupNumber", type=int, help="Número do grupo")
    args = parser.parse_args()

    IDJogo = args.IDJogo
    groupNumber = args.groupNumber
    print(IDJogo)
    print(groupNumber)
    exe_path = os.path.join(os.getcwd(), "mazerun.exe")
    command = [exe_path, "22", "1", "4"]

    print(command)
    mqtt_client = setup_mqtt()
    payload = json.dumps({"grupo": groupNumber})
    mqtt_publish(mqtt_client, "pisid_keepalive_22", payload)

    get_corridors(IDJogo)
    normalnoise, noisevartoleration = get_setupmaze(IDJogo)

    if normalnoise is None or noisevartoleration is None:
        print("Erro ao carregar dados de setupmaze. Encerrando...")
        return

    process = start_game_executable(command)
    monitor_game(IDJogo, groupNumber,process, mqtt_client, normalnoise, noisevartoleration)

if __name__ == "__main__":
    main()