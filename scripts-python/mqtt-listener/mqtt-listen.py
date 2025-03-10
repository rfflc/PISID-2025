#recebe arugumetos --server, --port e --topic. Os primeiros dois podem ser omitidos pois tem valor default
#To-Do:tratamento de dados (erros, outliers, dados repetidos, desvio padrão)
#To-Do: registar mongoDb 

import paho.mqtt.client as mqtt
import argparse


# Callback when a message is received
def on_message(client, userdata, message):
    print(f"Received message: {message.payload.decode()} on topic {message.topic}")

# Callback when connected to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully!")
        client.subscribe(mqtt_topic)
        print(f"Subscribed to topic: {mqtt_topic}")
    else:
        print(f"Failed to connect, return code {rc}")

# MQTT Configuration from agrs
parser = argparse.ArgumentParser(description="MQTT topic")
parser.add_argument("--server",help="Provides mqtt server", type=str, default="broker.mqtt-dashboard.com")
parser.add_argument("--port", type=int, default=1883)
parser.add_argument("--topic",help="Provides mqtt topic to subscribe", type=str)

args = parser.parse_args()
cloud_server = args.server
port = args.port
mqtt_topic = args.topic


# Create MQTT client instance
client = mqtt.Client()

# Assign callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect(cloud_server, port, 60)

# Start the loop to process messages
print("Listening for messages...")
client.loop_forever()
