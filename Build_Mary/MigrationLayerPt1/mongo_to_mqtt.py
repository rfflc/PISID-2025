# mongo_to_mqtt.py
import time  
import json  
import pymongo  
import paho.mqtt.client as mqtt  

# configuration
def load_config(config_path="config.json"):  
    try:  
        with open(config_path) as f:  
            return json.load(f)  
    except FileNotFoundError:  
        print(f"FATAL ERROR: Missing config file '{config_path}'")  
        exit(1)  

config = load_config()  

# mongoDB connection
def get_mongo_collections():  
    client = pymongo.MongoClient(config["mongo_uri"])  
    db = client[config["mongo_db"]]  
    return {  
        "sound": db.soundLevels,  
        "movement": db.movements  
    }  

# MQTT publishing   
def publish_to_mqtt(client, topic_suffix, payload):  
    player_id = payload["Player"]  
    topic = f"pisid_maze{topic_suffix}_{player_id}"  
    client.publish(topic, str(payload))  
    print(f"Published to {topic}: {payload}")  

# main migration logic
def migrate():  
    mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)  
    mqtt_client.connect(config["mqtt_broker"], config["mqtt_port"])  
    collections = get_mongo_collections()  

    while True:  
        # process sound data  
        for doc in collections["sound"].find({"Migrated": False}):  
            try:  
                payload = {  
                    "Player": doc["Player"],  
                    "Hour": doc["Hour"],  
                    "Sound": doc["SoundLevel"]  
                }  
                publish_to_mqtt(mqtt_client, "sound", payload)  
            except Exception as e:  
                print(f"SOUND ERROR (doc {doc['_id']}): {str(e)}")  
            finally:  
                collections["sound"].update_one(  
                    {"_id": doc["_id"]},  
                    {"$set": {"Migrated": True}}  
                )  

        # process movement data  
        for doc in collections["movement"].find({"Migrated": False}):  
            try:  
                payload = {  
                    "Player": doc["Player"],  
                    "Marsami": doc["Marsami"],  
                    "RoomOrigin": doc["RoomOrigin"],  
                    "RoomDestiny": doc["RoomDestiny"],  
                    "Status": doc["Status"]  
                }  
                publish_to_mqtt(mqtt_client, "mov", payload)  
            except Exception as e:  
                print(f"MOVEMENT ERROR (doc {doc['_id']}): {str(e)}")  
            finally:  
                collections["movement"].update_one(  
                    {"_id": doc["_id"]},  
                    {"$set": {"Migrated": True}}  
                )  

        time.sleep(1)  

if __name__ == "__main__":  
    migrate()  