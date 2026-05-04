# mongo_to_mqtt_mt.py  
import time  
import json  
import threading  
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

# mongo connection
def get_mongo_collections():  
    client = pymongo.MongoClient(config["mongo_uri"])  
    db = client[config["mongo_db"]]  
    return {  
        "sound": db.soundLevels,  
        "movement": db.movements  
    }  

# shared publishing function  
def publish_to_mqtt(client, topic_suffix, payload):  
    player_id = payload["Player"]  
    topic = f"pisid_maze{topic_suffix}_PC2"  
    client.publish(topic, str(payload), qos=1)  
    print(f"Published to {topic}: {payload}")  

# thread 1 - sound processing  
def sound_worker():  
    mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)  
    mqtt_client.connect(config["mqtt_broker"], config["mqtt_port"])  
    sound_col = get_mongo_collections()["sound"]  
    
    while True:  
        try:  
            for doc in sound_col.find({"Migrated": False}):  
                try:  
                    payload = {  
                        "Player": doc["Player"],  
                        "Hour": doc["Hour"],  
                        "Sound": doc["SoundLevel"]  
                    }  
                    publish_to_mqtt(mqtt_client, "sound", payload)  
                except Exception as e:  
                    print(f"SOUND THREAD ERROR: {str(e)}")  
                finally:  
                    sound_col.update_one(  
                        {"_id": doc["_id"]},  
                        {"$set": {"Migrated": True}}  
                    )  
        except Exception as e:  
            print(f"SOUND THREAD CRITICAL ERROR: {str(e)}")  
        time.sleep(0.5)  

# thread 2 - movement processing  
def movement_worker():  
    mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)  
    mqtt_client.connect(config["mqtt_broker"], config["mqtt_port"])  
    mov_col = get_mongo_collections()["movement"]  
    
    while True:  
        try:  
            for doc in mov_col.find({"Migrated": False}):  
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
                    print(f"MOVEMENT THREAD ERROR: {str(e)}")  
                finally:  
                    mov_col.update_one(  
                        {"_id": doc["_id"]},  
                        {"$set": {"Migrated": True}}  
                    )  
        except Exception as e:  
            print(f"MOVEMENT THREAD CRITICAL ERROR: {str(e)}")  
        time.sleep(0.5)  

if __name__ == "__main__":  
    # start threads  
    sound_thread = threading.Thread(target=sound_worker, daemon=True)  
    movement_thread = threading.Thread(target=movement_worker, daemon=True)  
    
    sound_thread.start()  
    movement_thread.start()  
    
    # keep main thread alive  
    try:  
        while True:  
            time.sleep(1)  
    except KeyboardInterrupt:  
        print("\nMigration stopped by user")  