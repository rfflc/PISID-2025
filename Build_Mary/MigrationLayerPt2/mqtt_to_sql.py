# mqtt_to_mysql.py
import json
import pymysql
import paho.mqtt.client as mqtt
from datetime import datetime

# load config
def load_config(config_path="config.json"):
    try:
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"FATAL ERROR: Missing config file '{config_path}'")
        exit(1)

config = load_config()

# mysql connection
def get_mysql_conn():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="maze",
        cursorclass=pymysql.cursors.DictCursor
    )

# mqtt handlers
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT with code {reason_code}")
    client.subscribe("pisid_mazesound_22")
    client.subscribe("pisid_mazemov_22")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Received: {payload}")
        
        conn = get_mysql_conn()
        with conn.cursor() as cursor:
            if "Sound" in payload:  # sound data
                cursor.callproc("sp_MigrateSound", [
                    f"{datetime.now().timestamp()}",  # generate unique ID
                    payload["Player"],
                    payload["Hour"],
                    payload["Sound"],
                    1  # jogo_id (replace with actual game ID)
                ])
            elif "Marsami" in payload:  # movement data
                cursor.callproc("sp_MigrateMovements", [
                    f"{datetime.now().timestamp()}",  # generate unique ID
                    payload["Player"],
                    payload["Marsami"],
                    payload["RoomOrigin"],
                    payload["RoomDestiny"],
                    payload["Status"],
                    1  # jogo_id (replace with actual game ID)
                ])
            conn.commit()
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        conn.close()

# main
if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(config["mqtt_broker"], config["mqtt_port"])
    client.loop_forever()