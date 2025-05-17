import subprocess
import time
import os
import json
import signal
import paho.mqtt.client as mqtt
import platform

#Configurações
TOPICO_MQTT = "pisid_keeplive_22"
BROKER = "broker.emqx.io"
PORT = 1883

#Placeholders
processos = {}
ultimo_grupo = None  # grupo ativo

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
        return subprocess.Popen(['python3', script_path, str(grupo)])


def terminar_processos():
    global processos
    for nome, proc in processos.items():
        if proc and proc.poll() is None:
            print(f"[INFO] Terminando {nome}.py")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    processos = {}  # Limpar lista de processos

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("[MQTT] Conectado ao broker.")
    client.subscribe(TOPICO_MQTT)

def on_message(client, userdata, msg):
    global processos, ultimo_grupo
    print(f"[MQTT] Mensagem recebida: {msg.payload.decode()}")

    try:
        data = json.loads(msg.payload.decode())

        if "grupo" in data:
            grupo = data["grupo"]
            ultimo_grupo = grupo

            if "layer1" not in processos or processos["layer1"].poll() is not None:
                processos["layer1"] = iniciar_script("layer1", grupo)

            if "mongo_to_mqtt" not in processos or processos["mongo_to_mqtt"].poll() is not None:
                processos["mongo_to_mqtt"] = iniciar_script("mongo_to_mqtt", grupo)

        elif "end" in data and data["end"] == True:
            print("[MQTT] Comando de fim recebido.")
            terminar_processos()
            ultimo_grupo = None

    except json.JSONDecodeError:
        print("[ERRO] JSON inválido.")
    except Exception as e:
        print(f"[ERRO] Erro ao processar mensagem: {e}")

def main():
    global ultimo_grupo
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT)
    client.loop_start()

    print(f"[KEEPALIVE] A escutar: {TOPICO_MQTT}")

    try:
        while True:
            time.sleep(5)
            for nome in ["layer1", "mongo_to_mqtt"]:
                proc = processos.get(nome)
                if proc and proc.poll() is not None:
                    print(f"[WARN] {nome}.py caiu. Reiniciando...")
                    if ultimo_grupo is not None:
                        processos[nome] = iniciar_script(nome, ultimo_grupo)

    except KeyboardInterrupt:
        print("\n[KEEPALIVE] Encerrado manualmente.")
        terminar_processos()
    finally:
        client.loop_stop()

if __name__ == "__main__":
    main()
