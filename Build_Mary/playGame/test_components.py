import subprocess
import time
import paho.mqtt.client as mqtt
import json

def start_game_executable(path, iDJogo):
    return subprocess.Popen([path, str(iDJogo)],
                            creationflags=subprocess.CREATE_NEW_CONSOLE)
def start_data_executable(path, iDJogo):
    return subprocess.Popen([path, str(iDJogo)],
                            creationflags=subprocess.CREATE_NEW_CONSOLE)

def monitor_game(iDJogo, exe_process, mqtt_client):
    try:
        while exe_process.poll() is None:
            #check_sound_and_rooms(iDJogo, mqtt_client)
            time.sleep(2)  # adjust as needed
    except Exception as e:
        print(f"Erro durante o jogo: {e}")
    finally:
        #mark_game_as_terminated(iDJogo)
        print("Jogo terminado")

#CRIA UM CLIENT MQTT E PUBLICA
def mqtt_publish(client, topic, message):
    client.publish(topic, json.dumps(message))

def setup_mqtt():
    client = mqtt.Client()
    client.connect("broker.mqttdashboard.com", 1883)
    return client

#process_data = start_data_executable("c:\\mazerun\\mazerun.exe")
#process = start_game_executable("c:\\mazerun\\mazerun.exe", 22)
#monitor_game(1, process, "")
client = setup_mqtt()
message1 = {
                "Type": "Score",
                "Player": 22,
                "Room": 1
            }

message2 = {
                "Type": "CloseAllDoor",
                "Player": 22
            }


mqtt_publish(client, "pisid_ mazeact", message1)
mqtt_publish(client, "pisid_ mazeact", message2)

user_input = input("Enter a command or message: ")
message3 = {
                "Type": "Score",
                "Player": "22",
                "Room": user_input
            }
mqtt_publish(client, "pisid_ mazeact", message3)