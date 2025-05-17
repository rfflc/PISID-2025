# mqtt_to_sql.py
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


# SQL connection
def get_mysql_conn():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="pisid",
        cursorclass=pymysql.cursors.DictCursor,
    )


# json parsing
def safe_json_parse(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try fixing common issues
        fixed = raw.replace("'", '"').replace("True", "true").replace("False", "false")
        return json.loads(fixed)


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with code {reason_code}")
    client.subscribe("pisid_mazesound_PC2")
    client.subscribe("pisid_mazemov_PC2")


def on_message(client, userdata, message):
    raw_payload = message.payload.decode()
    print(f"Raw payload: {raw_payload}")
    conn = None
    try:
        # JSON parsing and validation logic
        payload = safe_json_parse(raw_payload)
        required_fields = {
            "sound": ["Player", "Hour", "Sound"],
            "movement": ["Player", "Marsami", "RoomOrigin", "RoomDestiny", "Status"],
        }

        payload_type = (
            "sound"
            if "Sound" in payload
            else "movement" if "Marsami" in payload else None
        )
        if not payload_type:
            raise ValueError("Unknown payload type")

        missing = [f for f in required_fields[payload_type] if f not in payload]
        if missing:
            raise ValueError(f"Missing fields: {missing}")

        # database operations
        conn = get_mysql_conn()
        with conn.cursor() as cursor:
            if payload_type == "sound":
                cursor.execute(
                    """
                    INSERT INTO sound (id_sound, player, hour, soundlevel, idjogo)
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
            else:
                cursor.execute(
                    """
                    INSERT INTO medicoespassagens 
                    (id_medicao, player, marsami, roomorigin, roomdestiny, status, idjogo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        f"{datetime.now().timestamp()}",
                        payload["Player"],
                        payload["Marsami"],
                        payload["RoomOrigin"],
                        payload["RoomDestiny"],
                        payload["Status"],
                        2,  # hardcoded jogo_id=1
                    ],
                )
                # call stored procedure to update room occupancy
                cursor.callproc(
                    "sp_UpdateRoomOccupancy",
                    (
                        2,
                        payload["Marsami"],
                        payload["RoomOrigin"],
                        payload["RoomDestiny"],
                    ),
                )
                conn.commit()
        print(f"Processed {payload_type} payload")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        try:
            conn = get_mysql_conn()
            with conn.cursor() as cursor:
                error_data = {"raw_payload": raw_payload, "error": str(e)}
                if "sound" in raw_payload.lower():
                # if "Sound" in raw_payload:
                    print(f"DEBUG - Raw Payload (Type: {type(raw_payload)}): {raw_payload}")
                    cursor.execute(
                        """
                        INSERT INTO advanced_outliers_sound 
                        (player_id, soundlevel, hour, errorreason)
                        VALUES (%(Player)s, %(Sound)s, %(Hour)s, %(error)s)
                        """,
                        {**payload, **error_data},
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO advanced_outliers_movements 
                        (marsami_id, roomorigin, roomdestiny, status, errorreason)
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


if __name__ == "__main__":
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(config["mqtt_broker"], config["mqtt_port"])
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nStopped by user")
