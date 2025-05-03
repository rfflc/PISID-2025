# mongo_to_mqtt.py 
import time  
import pymongo  
import paho.mqtt.client as mqtt  
from datetime import datetime  

# configuration  
MONGO_URI = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"  
MONGO_DB = "sensordata"  
MQTT_BROKER = "broker.emqx.io"  
MQTT_PORT = 1883  

def get_mongo_collections():  
    client = pymongo.MongoClient(MONGO_URI)  
    db = client[MONGO_DB]  
    return {  
        "sound": db.soundLevels,  
        "movement": db.movements  
    }  

def publish_to_mqtt(client, topic_suffix, payload):  
    topic = f"pisid_maze{topic_suffix}"  
    client.publish(topic, payload)  
    print(f"published to {topic}: {payload}")  

def migrate():  
    mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)  
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)  
    collections = get_mongo_collections()  

    while True:  
        # process sound data  
        for doc in collections["sound"].find({"Migrated": False}):  
            hour_str = doc["Hour"]  
            hour_obj = datetime.strptime(hour_str, "%Y-%m-%d %H:%M:%S.%f")  # Adjust format to match your data  
            payload = {  
                "Player": doc["Player"],  
                "Hour": hour_obj.isoformat(),  
                "Sound": doc["SoundLevel"]  
            }   
            publish_to_mqtt(mqtt_client, "sound", str(payload))  
            collections["sound"].update_one({"_id": doc["_id"]}, {"$set": {"Migrated": True}})  

        # process movement data  
        for doc in collections["movement"].find({"Migrated": False}):  
            payload = {  
                "Player": doc["Player"],  
                "Marsami": doc["Marsami"],  
                "RoomOrigin": doc["RoomOrigin"],  
                "RoomDestiny": doc["RoomDestiny"],  
                "Status": doc["Status"]  
            }  
            publish_to_mqtt(mqtt_client, "mov", str(payload))  
            collections["movement"].update_one({"_id": doc["_id"]}, {"$set": {"Migrated": True}})  

        time.sleep(5)  # poll every 5 seconds  

if __name__ == "__main__":  
    migrate()  