#!/usr/bin/env python3

# To run
# python .\MQTT_To_MYSQL.py --player 22

"""
mqtt_to_mysql.py  – Labirinto  |  Grupo 22
Consome MQTT da cloud e despacha para MySQL através das SPs
    • Som  →  CALL sp_InserirSom(...)
    • Move →  CALL sp_InserirMovimento(...)

Uso:
    python mqtt_to_mysql.py -p 22 \
        --mysql_host 194.210.86.10 --mysql_user aluno --mysql_pass aluno --mysql_db maze
"""

import argparse, json, re, sys
import paho.mqtt.client as mqtt
import mysql.connector as my

# ---------- CLI ----------
cli = argparse.ArgumentParser()
cli.add_argument("-p", "--player", type=int, required=True)
cli.add_argument("--broker", default="broker.emqx.io")
cli.add_argument("--port",   type=int, default=1883)
cli.add_argument("--mysql_host", default="localhost")
cli.add_argument("--mysql_user", default="root")
cli.add_argument("--mysql_pass", default="")
cli.add_argument("--mysql_db",   default="maze")
cfg = cli.parse_args()

PLAYER      = cfg.player
TOP_MOV     = f"pisid_mazemov_{PLAYER}"
TOP_SOUND   = f"pisid_mazesound_{PLAYER}"

# ---------- MySQL ----------
try:
    sql = my.connect(
        host     = cfg.mysql_host,
        user     = cfg.mysql_user,
        password = cfg.mysql_pass,
        database = cfg.mysql_db,
        autocommit = True       # SPs fazem o commit
    )
    cur = sql.cursor()
    print("✓ MySQL ligado")
except my.Error as e:
    print("MySQL error:", e); sys.exit(1)

# ---------- MQTT helpers ----------
re_key = re.compile(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:')

def fix_json(raw: bytes) -> dict | None:
    try:
        txt = raw.decode()
        txt = re_key.sub(r'\1"\2":', txt).replace("'", '"')
        return json.loads(txt)
    except Exception:
        return None

# ---------- callbacks ----------
def on_connect(c, _u, _f, rc):
    if rc == 0:
        print("✓ MQTT ligado")
        c.subscribe([(TOP_MOV,0),(TOP_SOUND,0)])
    else:
        print("Falha MQTT:", rc)

def on_message(_c, _u, m):
    d = fix_json(m.payload)
    if not d:
        print("payload mal-formado → ignorado"); return

    try:
        if m.topic == TOP_SOUND:
            cur.callproc("sp_InserirSom", (
                d.get("Id" ,  d["Hour"]),             # id_sound   (usa Hour se não vier Id)
                int(d["Player"]),
                d["Hour"],
                float(d["Sound"]),
                1                                      # assumimos jogo_id=1 (ajuste se necessário)
            ))
            print("som OK")
        else:
            cur.callproc("sp_InserirMovimento", (
                d.get("Id",  f'{d["Player"]}-{d["Marsami"]}-{d["RoomOrigin"]}-{d["RoomDestiny"]}'),
                int(d["Player"]),
                int(d["Marsami"]),
                int(d["RoomOrigin"]),
                int(d["RoomDestiny"]),
                int(d["Status"]),
                1
            ))
            print("mov OK")
    except (KeyError, ValueError) as bad:
        print("campos em falta/valor errado → ignorado:", bad)
    except my.Error as e:
        print("MySQL SP erro:", e)

# ---------- run ----------
mqttc = mqtt.Client(f"mysql_writer_{PLAYER}")
mqttc.on_connect, mqttc.on_message = on_connect, on_message
mqttc.connect(cfg.broker, cfg.port, 60)
mqttc.loop_forever()
