# mqtt_to_sql_mt.py
import json
import pymysql
import pymysql.cursors
import paho.mqtt.client as mqtt
from datetime import datetime
import threading


# load config
def load_config(config_path="config.json"):
    try:
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"FATAL ERROR: Missing config file '{config_path}'")
        exit(1)


config = load_config()


# SQL connection
def get_mysql_conn():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="pisid",
        database="maze",
        cursorclass=pymysql.cursors.DictCursor,
    )


# json parsing
def safe_json_parse(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        fixed = raw.replace("'", '"').replace("True", "true").replace("False", "false")
        return json.loads(fixed)


def process_sound_message(payload, raw_payload):
    conn = None
    try:
        conn = get_mysql_conn()
        with conn.cursor() as cursor:
            cursor.execute(
                """
    INSERT INTO sound (id_sound, player, hour, soundLevel, IDJogo)
    VALUES (%s, %s, %s, %s, %s)
""",
                [
                    f"{datetime.now().timestamp()}",
                    payload["Player"],
                    payload["Hour"],
                    payload["Sound"],
                    1,  # hardcoded jogo_id=1
                ],
            )
            conn.commit()
        print("Processed sound payload")
    except Exception as e:
        handle_error(e, raw_payload, "sound")
    finally:
        if conn:
            conn.close()


def process_movement_message(payload, raw_payload):
    conn = None
    try:
        conn = get_mysql_conn()
        with conn.cursor() as cursor:
            cursor.execute(
                """
    INSERT INTO medicoespassagens 
    (id_medicao, player, marsami, roomOrigin, roomDestiny, status, IDJogo)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
""",
                [
                    f"{datetime.now().timestamp()}",
                    payload["Player"],
                    payload["Marsami"],
                    payload["RoomOrigin"],
                    payload["RoomDestiny"],
                    payload["Status"],
                    1,  # hardcoded jogo_id=1
                ],
            )
            conn.commit()
        print("Processed movement payload")
    except Exception as e:
        handle_error(e, raw_payload, "movement")
    finally:
        if conn:
            conn.close()


def handle_error(e, raw_payload, payload_type):
    print(f"ERROR: {str(e)}")
    try:
        conn = get_mysql_conn()
        with conn.cursor() as cursor:
            error_data = {"raw_payload": raw_payload, "error": str(e)}

            if payload_type == "sound":
                cursor.execute(
                    """
                    INSERT INTO advanced_outliers_sound 
                    (player_id, sound_level, hour, error_reason)
                    VALUES (%(Player)s, %(Sound)s, %(Hour)s, %(error)s)
                    """,
                    {**payload, **error_data},
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO advanced_outliers_movements 
                    (marsami_id, room_origin, room_destiny, status, error_reason)
                    VALUES (%(Marsami)s, %(RoomOrigin)s, %(RoomDestiny)s, %(Status)s, %(error)s)
                    """,
                    {**payload, **error_data},
                )
            conn.commit()
    except Exception as db_error:
        print(f"DB ERROR: {db_error}")
    finally:
        if conn:
            conn.close()


def sound_worker():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = lambda c, *args: c.subscribe("pisid_mazesound_22")

    def on_message(client, userdata, message):
        raw = message.payload.decode()
        try:
            payload = safe_json_parse(raw)
            if "Sound" not in payload:
                raise ValueError("Missing Sound field")
            process_sound_message(payload, raw)
        except Exception as e:
            handle_error(e, raw, "sound")

    client.on_message = on_message
    client.connect(config["mqtt_broker"], config["mqtt_port"])
    client.loop_forever()


def movement_worker():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = lambda c, *args: c.subscribe("pisid_mazemov_22")

    def on_message(client, userdata, message):
        raw = message.payload.decode()
        try:
            payload = safe_json_parse(raw)
            if "Marsami" not in payload:
                raise ValueError("Missing Marsami field")
            process_movement_message(payload, raw)
        except Exception as e:
            handle_error(e, raw, "movement")

    client.on_message = on_message
    client.connect(config["mqtt_broker"], config["mqtt_port"])
    client.loop_forever()


if __name__ == "__main__":
    sound_thread = threading.Thread(target=sound_worker, daemon=True)
    movement_thread = threading.Thread(target=movement_worker, daemon=True)

    sound_thread.start()
    movement_thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nStopped by user")
