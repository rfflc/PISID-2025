import subprocess
import time
import os
import json
import signal
import platform
import paho.mqtt.client as mqtt
import psutil  # pip install psutil


#####################codigolayer2###################
main
self.last_sound_time = time.time()
self.last_movement_time = time.time()
self.game_ended = False
self.start_inactivity_monitor()

def start_inactivity_monitor(self):
    def monitor():
        while True:
            time.sleep(1)
            now = time.time()
            no_sound = now - self.last_sound_time > 10
            no_movement = now - self.last_movement_time > 10

            if not self.game_ended and no_sound and no_movement:
                print("[INFO] Inatividade total detectada. A enviar fim de jogo...")
                self.client.publish("pisid_mazeact", json.dumps({"Type": "End", "Player": 22}))
                self.game_ended = True

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()

#adionar ao on message:
if "Sound" in data:
    self.last_sound_time = time.time()
if "Marsami" in data:
    self.last_movement_time = time.time()



def fechar_aba_terminal_mac():
    if platform.system() == "Darwin":
        subprocess.Popen([
            "osascript", "-e",
            'tell application "System Events" to keystroke "w" using {command down}'
        ])
# Configurações MQTT
TOPICO_MQTT = "pisid_keepalive_22"
BROKER = "broker.emqx.io"
PORT = 1883

# Estado
processos = {}
ultimo_grupo = None

def iniciar_script(nome, grupo):
    print(f"[INFO] Iniciando {nome}.py com grupo {grupo}")
    script_path = os.path.abspath(f"{nome}.py")
    script_dir = os.path.dirname(script_path)
    sistema = platform.system()

    if sistema == "Windows":
        return subprocess.Popen(
            ['cmd', '/c', 'start', 'cmd', '/k', f'cd /d {script_dir} && python {nome}.py {grupo}']
        )

    elif sistema == "Darwin":
        return subprocess.Popen([
            "osascript", "-e",
            f'tell application "Terminal" to do script "cd \\"{script_dir}\\" && python3 \\"{nome}.py\\" {grupo}"'
        ])

    else:
        # Linux ou outro
        return subprocess.Popen(['python3', script_path, str(grupo)])

def script_esta_ativo(nome):
    lock_path = os.path.abspath(f"{nome}.lock")
    if not os.path.exists(lock_path):
        return False
    try:
        with open(lock_path) as f:
            pid = int(f.read().strip())
        return psutil.pid_exists(pid)
    except:
        return False

def terminar_processos():
    print("[INFO] Terminando scripts ativos...")
    for nome in ["layer1", "mongo_to_mqtt"]:
        lock_path = os.path.abspath(f"{nome}.lock")
        if os.path.exists(lock_path):
            try:
                with open(lock_path) as f:
                    pid = int(f.read().strip())
                print(f"[INFO] Terminando {nome}.py (PID {pid})")
                os.kill(pid, signal.SIGTERM)
            except Exception as e:
                print(f"[WARN] Não consegui terminar {nome}: {e}")
        else:
            print(f"[INFO] Nenhum lock ativo para {nome}")
    processos.clear()

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("[MQTT] Ligado ao broker MQTT.")
    client.subscribe(TOPICO_MQTT)

def on_message(client, userdata, msg):
    global ultimo_grupo
    print(f"[MQTT] Mensagem recebida: {msg.payload.decode()}")

    try:
        data = json.loads(msg.payload.decode())

        if "grupo" in data:
            grupo = data["grupo"]
            ultimo_grupo = grupo  # memoriza grupo

            for nome in ["layer1", "mongo_to_mqtt"]:
                if not script_esta_ativo(nome):
                    iniciar_script(nome, grupo)

        elif "end" in data and data["end"] == True:
            print("[MQTT] Comando de fim recebido.")
            terminar_processos()
            ultimo_grupo = None

    except json.JSONDecodeError:
        print("[ERRO] JSON inválido.")
    except Exception as e:
        print(f"[ERRO] Falha ao processar mensagem: {e}")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT)
    client.loop_start()

    print(f"[KEEPALIVE] A escutar tópico: {TOPICO_MQTT}")

    try:
        while True:
            time.sleep(5)
            if ultimo_grupo:
                for nome in ["layer1", "mongo_to_mqtt"]:
                    if not script_esta_ativo(nome):
                        print(f"[WARN] {nome}.py inativo. Reiniciando...")
                        iniciar_script(nome, ultimo_grupo)
    except KeyboardInterrupt:
        print("\n[KEEPALIVE] Interrompido manualmente.")
        terminar_processos()
    finally:
        client.loop_stop()

if __name__ == "__main__":
    main()
