# # To run
# # python Mongo_To_MQTT.py --player 22

# import json
# import time
# import pymongo
# import paho.mqtt.client as mqtt
# from pymongo import UpdateOne

# class MongoToMqttMigrator:
#     def __init__(self, player, mongo_uri="mongodb://localhost:27017/", broker="broker.emqx.io", port=1883, interval=1.0):
#         self.player = player
#         self.mongo_uri = mongo_uri
#         self.broker = broker
#         self.port = port
#         self.interval = interval
#         self.mov_topic = f"pisid_mazemov_{player}"
#         self.snd_topic = f"pisid_mazesound_{player}"

#         # MongoDB setup
#         self.mongo = pymongo.MongoClient(mongo_uri)
#         db = self.mongo["labirinto"]
#         self.mov_col = db.movements
#         self.snd_col = db.soundLevels
#         self.mov_col.create_index("Migrated")
#         self.snd_col.create_index("Migrated")

#         # MQTT setup
#         self.mqtt_client = mqtt.Client(f"sender_{player}")
#         self.mqtt_client.on_connect = self.on_connect
#         self.mqtt_client.connect(broker, port, 60)
#         self.mqtt_client.loop_start()

#     def on_connect(self, client, userdata, flags, rc):
#         if rc == 0:
#             print("MQTT connected")
#         else:
#             print(f"MQTT connection failed: {rc}")

#     def publish_documents(self, collection, topic, required_fields):
#         docs = list(collection.find({"Migrated": False, "Player": self.player}))
#         if not docs:
#             return

#         updates = []
#         for doc in docs:
#             if not required_fields.issubset(doc):
#                 print("Invalid doc:", doc)
#                 continue
#             payload = doc.copy()
#             payload.pop("_id", None)
#             try:
#                 self.mqtt_client.publish(topic, json.dumps(payload), qos=0)
#                 updates.append(UpdateOne({"_id": doc["_id"]}, {"$set": {"Migrated": True}}))
#                 print(f"Sent to {topic}: {payload}")
#             except Exception as e:
#                 print(f"Failed MQTT publish: {e}")

#         if updates:
#             collection.bulk_write(updates)
#             print(f"{len(updates)} marked as Migrated")

#     def run(self):
#         try:
#             while True:
#                 self.publish_documents(self.mov_col, self.mov_topic, {"Player", "Marsami", "RoomOrigin", "RoomDestiny", "Status"})
#                 self.publish_documents(self.snd_col, self.snd_topic, {"Player", "Hour", "Sound"})
#                 time.sleep(self.interval)
#         except KeyboardInterrupt:
#             print("Shutting down...")
#         finally:
#             self.mqtt_client.loop_stop()

# migrator = MongoToMqttMigrator(player=22)
# migrator.run()
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
    topic = f"pisid_maze{topic_suffix}_{player_id}"  
    client.publish(topic, str(payload), qos=1)  
    print(f"Published to {topic}: {payload}")  

# thread 1 - sound processing  
def sound_worker():  
    mqtt_client = mqtt.Client()  
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
    mqtt_client = mqtt.Client()  
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