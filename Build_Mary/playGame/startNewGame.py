import paho.mqtt.client as mqtt
import subprocess
import mysql.connector
import sqlite3
import time
import sys

from mysql.connector import Error

# Argumentos da linha de comando
if len(sys.argv) < 3:
    print("Uso: python script.py <numero_grupo> <id_jogador>")
    sys.exit(1)

numero_grupo = sys.argv[1]
id_jogador = sys.argv[2]

# CONFIGURAÇÕES
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "jogo/sensores"
DB_PATH = "jogo.db"
GAME_EXECUTABLE = "./meu_jogo_runable"

# DB externas
DB_MAZE_CONFIG = {
    'host': '194.210.86.10',
    'port': 3306,
    'user': 'usuario_maze',
    'password': 'senha_maze',
    'database': 'maze'
}

DB_PISID_CONFIG = {
    'host': '12.0.0.1',
    'port': 3306,
    'user': 'usuario_pisid',
    'password': 'senha_pisid',
    'database': 'pisid'
}


# FUNÇÃO PARA INICIAR MQTT
def iniciar_mqtt():
    def on_connect(client, userdata, flags, rc):
        print(f"Conectado ao MQTT com código {rc}")
        client.subscribe(MQTT_TOPIC)

    def on_message(client, userdata, msg):
        print(f"Mensagem recebida: {msg.topic} {msg.payload.decode()}")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    return client


# FUNÇÃO PARA INICIAR O JOGO
def iniciar_jogo():
    print("Iniciando jogo...")
    subprocess.Popen([GAME_EXECUTABLE])
    time.sleep(5)


# FUNÇÃO PARA CONECTAR À BASE DE DADOS LOCAL
def conectar_banco_local():
    print("Conectando ao banco de dados local...")
    conn = sqlite3.connect(DB_PATH)
    return conn


# FUNÇÃO PARA LER VALORES DO JOGO
def verificar_valores_jogo(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT ruido, localizacao FROM jogo_estados ORDER BY id DESC LIMIT 1")
    resultado = cursor.fetchone()
    if resultado:
        ruido, localizacao = resultado
        print(f"Nível de Ruído: {ruido}, Localização de Marsamis: {localizacao}")
        return ruido, localizacao
    return None, None


# ATUADORES
def usar_actuadores(ruido, localizacao):
    if ruido > 80:
        print("Atuador: Reduzindo volume...")
    if localizacao == "zona_insegura":
        print("Atuador: Ativando alerta!")


# FUNÇÃO PARA COPIAR DADOS DE maze PARA pisid
def copiar_setupmaze(iDJogo):
    try:
        print("Ligando ao banco maze...")
        maze_conn = mysql.connector.connect(**DB_MAZE_CONFIG)
        pisid_conn = mysql.connector.connect(**DB_PISID_CONFIG)

        maze_cursor = maze_conn.cursor(dictionary=True)
        pisid_cursor = pisid_conn.cursor()

        maze_cursor.execute("SELECT * FROM setupmaze LIMIT 1")
        dados = maze_cursor.fetchone()

        if not dados:
            print("Nenhum dado encontrado na base maze.")
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

        print("Dados inseridos na base pisid com sucesso.")

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
    mqtt_client = iniciar_mqtt()
    iniciar_jogo()
    conn_local = conectar_banco_local()

    copiar_setupmaze(id_jogador)

    try:
        while True:
            ruido, localizacao = verificar_valores_jogo(conn_local)
            if ruido is not None and localizacao is not None:
                usar_actuadores(ruido, localizacao)
            time.sleep(10)
    except KeyboardInterrupt:
        print("Encerrando...")
    finally:
        conn_local.close()
        mqtt_client.loop_stop()


if __name__ == "__main__":
    main()
