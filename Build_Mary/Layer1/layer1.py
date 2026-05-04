# layer1.py  
import json  
import sys  
from pymongo import MongoClient  
import paho.mqtt.client as mqtt  
import re


# configuration
def load_config(config_path="config.json"):  
    """load settings from json file"""  
    try:  
        with open(config_path) as f:  
            return json.load(f)  
    except FileNotFoundError:  
        print(f"error: config file {config_path} not found")  
        sys.exit(1)  


# data validation
def validate_sound_data(data):  
    """basic validation for sound sensor data"""  
    errors = []  
    # required fields  
    for field in ["Player", "Hour", "SoundLevel"]:  
        if field not in data:  
            errors.append(f"missing field: {field}")  

    # basic value checks
    sound_level = data.get("SoundLevel", 0)  
    if sound_level < 0:  
        errors.append("soundLevel cannot be negative")  
    if sound_level > 30:  
        errors.append("soundLevel exceeds 30")  
    if data.get("Player", 0) <= 0:  
        errors.append("invalid player ID")  

    return errors  

def validate_movement_data(data):  
    """basic validation for movement data"""  
    errors = []  
    # required fields  
    for field in ["Player", "Marsami", "RoomOrigin", "RoomDestiny", "Status"]:  
        if field not in data:  
            errors.append(f"missing field: {field}")  

    # basic value checks  
    status = data.get("Status", -1)  
    if status not in [0, 1, 2]:  
        errors.append("invalid status code")  
    elif data.get("RoomOrigin") == data.get("RoomDestiny"):  
        # only allow same room if status indicates final position  
        if status != 0 and status != 2:  
            errors.append("roomOrigin and roomDestiny can only match for status 0/2")  

    return errors   


# mongoDB operations
class MongoDBHandler:  
    def __init__(self, config):  
        self.client = MongoClient(config["mongodb_uri"])  
        self.db = self.client[config["mongodb_db"]]  

    def save_to_mongodb(self, data, collection):  
        """insert data with auto-generated _id"""  
        data["Migrated"] = False  # flag for migration layer  
        self.db[collection].insert_one(data)  

    def save_outlier(self, data, collection):  
        """save invalid data to outlier collection"""  
        self.db[f"outliers_{collection}"].insert_one(data)  


# MQTT handling
class MQTTClient:  
    def __init__(self, config, mongo_handler):  
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)  # fix API version
        self.config = config  
        self.mongo = mongo_handler  
        self.client.on_connect = self.on_connect  
        self.client.on_message = self.on_message  

    def on_connect(self, client, userdata, flags, reason_code, properties):  # updated signature
        if reason_code == 0:  
            print(f"connected to MQTT broker")  
            client.subscribe("pisid_mazemov_22")  
            client.subscribe("pisid_mazesound_22")  
        else:  
            print(f"connection failed: {reason_code}") 

    def on_message(self, client, userdata, msg):  
        try:  
            payload = msg.payload.decode()  
            
            # fix unquoted keys only at JSON structure level  
            fixed_payload = re.sub(r'(?<={|,)\s*(\w+):', r'"\1":', payload)  
            
            # debug: show intermediate fix  
            print(f"after key fix: {fixed_payload}")  
            
            # insert missing commas between key-value pairs  
            fixed_payload = re.sub(  
                r'("[^"]+":\s*[^,{]+)(\s*"[^"]+":)',  
                r'\1,\2',  
                fixed_payload  
            )  
            
            # extract JSON substring  
            json_start = fixed_payload.find('{')  
            json_end = fixed_payload.rfind('}') + 1  
            json_str = fixed_payload[json_start:json_end].strip()  
            print(f"attempting to parse: {json_str}")  
            
            data = json.loads(json_str)  
            self.process_payload(data)  
            
        except Exception as e:  # BROAD EXCEPTION HANDLING  
            print(f"unexpected error: {str(e)}")  
            self.mongo.save_outlier({"raw_payload": payload}, "invalid_format")  

    def process_payload(self, data):
        """validate and route data without ID logic"""
        # normalize key names
        if "Sound" in data and "SoundLevel" not in data:  # only rename if SoundLevel doesn't exist
            data["SoundLevel"] = data.pop("Sound")
        
        # determine collection type
        if "SoundLevel" in data:
            errors = validate_sound_data(data)
            collection = "soundLevels"
        elif "Marsami" in data:
            errors = validate_movement_data(data)
            collection = "movements"
        else:
            errors = ["Unknown data format"]
            collection = "invalid_format"

        # act on validation results
        if errors:
            print(f"invalid data: {', '.join(errors)}")
            self.mongo.save_outlier(data, collection)
        else:
            self.mongo.save_to_mongodb(data, collection)
            print(f"inserted into {collection}")


# main execution  
if __name__ == "__main__":  
    config = load_config()  
    mongo = MongoDBHandler(config)  
    mqtt_client = MQTTClient(config, mongo)  
    mqtt_client.client.connect(config["mqtt_broker"], config["mqtt_port"], 60)  
    mqtt_client.client.loop_forever()  