# To run script
# python FiltrarDados_To_MONGO.py --player 22

# To run mazerun
# .\mazerun 22 1 1 broker.emqx.io 1883

import paho.mqtt.client as mqtt
import pymongo
import json
import argparse
import re
from collections import deque

# input do player
parser = argparse.ArgumentParser()
parser.add_argument("--player", "-p", type=int, required=True)
args = parser.parse_args()
player = args.player

# definições básicas
broker = "broker.emqx.io"
port = 1883
topic_mov = f"pisid_mazemov_{player}"
topic_sound = f"pisid_mazesound_{player}"

# conectar ao mongo
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["labirinto"]
mov = db["movements"]
sound = db["soundLevels"]
mov_out = db["outliersMovements"]
sound_out = db["outliersSoundLevels"]

# campos obrigatórios
mov_keys = ["Player", "Marsami", "RoomOrigin", "RoomDestiny", "Status"]
sound_keys = ["Player", "Hour", "Sound"]

# para verificar outliers
last_sounds = deque(maxlen=5)

# ajustar o formato json das mensagens
fix_keys = re.compile(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:')

def fix_json(payload):
    try:
        text = payload.decode()
        text = fix_keys.sub(r'\1"\2":', text)
        text = text.replace("'", '"')
        return json.loads(text)
    except:
        return None

def has_all_keys(d, keys):
    for k in keys:
        if k not in d:
            return False
    return True

def sound_is_outlier(val):
    if len(last_sounds) < 5:
        return False
    avg = sum(last_sounds) / len(last_sounds)
    return abs(val - avg) > 1.5

# quando conecta ao broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("ligado ao broker")
        client.subscribe([(topic_mov, 0), (topic_sound, 0)])
    else:
        print("erro ao ligar:", rc)

# quando recebe mensagem
def on_message(client, userdata, msg):
    doc = fix_json(msg.payload)
    if not doc:
        print("mensagem ruim")
        return

    if msg.topic == topic_mov:
        if has_all_keys(doc, mov_keys):
            if int(doc["Player"]) >= 0 and int(doc["Marsami"]) >= 0:
                mov.insert_one({**doc, "Migrated": False})
                print("mov OK")
                return
        mov_out.insert_one({**doc, "Migrated": False})
        print("mov OUT")

    elif msg.topic == topic_sound:
        if has_all_keys(doc, sound_keys):
            try:
                val = float(doc["Sound"])
                if val >= 0 and val <= 30 and not sound_is_outlier(val):
                    last_sounds.append(val)
                    sound.insert_one({**doc, "Migrated": False})
                    print("sound OK")
                    return
            except:
                pass
        sound_out.insert_one({**doc, "Migrated": False})
        print("sound OUT")

# iniciar mqtt
mqtt_client = mqtt.Client(f"receiver_{player}")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(broker, port, 60)
mqtt_client.loop_forever()


# import json, re, argparse
# from collections import deque

# import paho.mqtt.client as mqtt
# import pymongo

# # ────────────────────────── Config ──────────────────────────
# def load_cfg(path="cfg.json"):
#     with open(path) as f:
#         return json.load(f)

# cfg = load_cfg()

# parser = argparse.ArgumentParser()
# parser.add_argument("--player", type=int, required=True)
# parser.add_argument("--broker", default=cfg["mqtt_broker"])
# parser.add_argument("--port",   type=int, default=cfg["mqtt_port"])
# parser.add_argument("--mongo",  default=cfg["mongodb_uri"])
# args = parser.parse_args()

# PLAYER = args.player
# BROKER = args.broker
# PORT   = args.port
# MONGO_URI = args.mongo
# DB_NAME = cfg["mongodb_db"]
# TOPIC_MOV   = f"pisid_mazemov_{PLAYER}"
# TOPIC_SOUND = f"pisid_mazesound_{PLAYER}"

# # ──────────────────────── MongoDB setup ─────────────────────
# mongo = pymongo.MongoClient(MONGO_URI)
# db = mongo[DB_NAME]
# COL_MOV, COL_SND = db.movements, db.soundLevels
# COL_OMOV, COL_OSND = db.outliersMovements, db.outliersSoundLevels

# # ─────────────────────── Validação & helpers ─────────────────
# MOV_KEYS   = {"Player", "Marsami", "RoomOrigin", "RoomDestiny", "Status"}
# SOUND_KEYS = {"Player", "Hour", "Sound"}

# last_sounds = deque(maxlen=5)                 # janela p/ outliers
# re_key = re.compile(r'([{,]\s*)([A-Za-z_]\w*)\s*:')   # põe aspas nas chaves

# def to_json(raw: bytes):
#     try:
#         txt = re_key.sub(r'\1"\2":', raw.decode())
#         txt = txt.replace("'", '"')
#         return json.loads(txt)
#     except Exception:
#         return None

# def sound_is_outlier(v: float) -> bool:
#     if len(last_sounds) < 5:
#         return False
#     return abs(v - sum(last_sounds)/len(last_sounds)) > 1.5

# # ───────────────────────── Callbacks MQTT ───────────────────
# def on_connect(c, *_):
#     print("Ligado ao broker")
#     c.subscribe([(TOPIC_MOV,0), (TOPIC_SOUND,0)])

# def on_message(_c, _u, msg):
#     print(f"[DEBUG] topic: {msg.topic}, raw payload: {msg.payload}")  # ADD THIS
#     doc = to_json(msg.payload)
#     if not doc:
#         print("payload ilegível")
#         return

#     if msg.topic == TOPIC_MOV:
#         if MOV_KEYS.issubset(doc) and all(int(doc[k])>=0 for k in ("Player","Marsami")):
#             COL_MOV.insert_one({**doc, "Migrated": False})
#             print("mov OK")
#         else:
#             COL_OMOV.insert_one({**doc, "Migrated": False})
#             print("mov OUT")

#     elif msg.topic == TOPIC_SOUND:
#         try:
#             val = float(doc["Sound"])
#             ok  = SOUND_KEYS.issubset(doc) and 0 <= val <= 30 and not sound_is_outlier(val)
#         except Exception:
#             ok = False

#         if ok:
#             last_sounds.append(val)
#             COL_SND.insert_one({**doc, "Migrated": False})
#             print("sound OK")
#         else:
#             COL_OSND.insert_one({**doc, "Migrated": False})
#             print("sound OUT")

# # ─────────────────────────── Main loop ──────────────────────
# mqttc = mqtt.Client(f"listener_{PLAYER}")
# mqttc.on_connect, mqttc.on_message = on_connect, on_message
# mqttc.connect(BROKER, PORT, 60)
# mqttc.loop_forever()