# actuators.py
import json
import pymysql
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv

# load environment variables first
load_dotenv()


def load_config(config_path="config.json"):
    with open(config_path) as f:
        config = json.load(f)

    # Replace placeholder strings with actual environment variables
    return {
        "mysql_host": config["mysql_host"],
        "mysql_user": config["mysql_user"],
        "mysql_password": os.getenv(config["mysql_password"]),
        "mysql_db": config["mysql_db"],
        "mqtt_broker": os.getenv(config["mqtt_broker"]),
        "mqtt_port": int(os.getenv(config["mqtt_port"])),
    }


config = load_config()


# SQL connection
def get_db_connection():
    return pymysql.connect(
        host=config["mysql_host"],
        user=config["mysql_user"],
        password=config["mysql_password"],
        database=config["mysql_db"],
        cursorclass=pymysql.cursors.DictCursor,
    )


# handle door control commands
def handle_door_command(payload, conn):
    try:
        with conn.cursor() as cursor:
            cursor.callproc(
                "AbrirFechar_Porta",
                (
                    payload["Player"],  # idJogo
                    None,  # idUtilizador (optional, not used here)
                    payload.get("RoomOrigin", 0),  # roomA (default to 0 if missing)
                    payload.get("RoomDestiny", 0),  # roomB (default to 0 if missing)
                    "open" if payload["Type"] == "OpenDoor" else "closed",  # status
                ),
            )
            conn.commit()
            print(f"Processed {payload['Type']} command via SP")

    except Exception as e:
        print(f"Door command error: {str(e)}")
        conn.rollback()


# handle scoring triggers
def handle_score_trigger(payload, conn):
    try:
        with conn.cursor() as cursor:
            cursor.callproc(
                "Ativar_Gatilho",
                (
                    payload["Player"],  # idJogo
                    None,  # idUtilizador (optional, not used here)
                    payload["Room"],  # nomeSala
                ),
            )
            conn.commit()
            print("Score trigger processed via SP")

    except Exception as e:
        print(f"Score trigger error: {str(e)}")
        conn.rollback()


# MQTT message handler
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        conn = get_db_connection()

        if payload["Type"] in ("OpenDoor", "CloseDoor", "OpenAllDoor", "CloseAllDoor"):
            handle_door_command(payload, conn)
        elif payload["Type"] == "Score":
            handle_score_trigger(payload, conn)

    except json.JSONDecodeError:
        print("Invalid JSON payload")
    except KeyError as e:
        print(f"Missing field in payload: {str(e)}")
    except Exception as e:
        print(f"General error: {str(e)}")
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(config["mqtt_broker"], config["mqtt_port"])
    client.subscribe("pisid_mazeact")
    client.loop_forever()
