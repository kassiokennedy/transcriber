import sounddevice as sd
import json
import os

CONFIG_FILE = "config.json"
SAMPLE_RATE = 16000

def listar_dispositivos_entrada():
    dispositivos = sd.query_devices()
    vistos = set()
    unicos = []

    for i, d in enumerate(dispositivos):
        if d['max_input_channels'] > 0:
            nome = d['name']
            if nome not in vistos:
                vistos.add(nome)
                unicos.append((nome, i))

    print("\n🎧 Dispositivos de entrada disponíveis:")
    for idx, (nome, _) in enumerate(unicos):
        print(f"{idx}: {nome}")

    return unicos

def salvar_dispositivo(nome):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"device_name": nome}, f)

def carregar_dispositivo_salvo():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("device_name")
        except:
            return None
    return None

def encontrar_indice_por_nome(nome_procurado):
    for i, d in enumerate(sd.query_devices()):
        if d['name'] == nome_procurado and d['max_input_channels'] > 0:
            return i
    raise RuntimeError(f"❌ Dispositivo '{nome_procurado}' não encontrado.")

def verificar_sample_rate_compativel(device_index):
    try:
        sd.check_input_settings(device=device_index, samplerate=SAMPLE_RATE)
        return True
    except Exception as e:
        print(f"⚠️  Dispositivo incompatível com {SAMPLE_RATE} Hz: {e}")
        return False

def escolher_dispositivo():
    dispositivo_salvo = carregar_dispositivo_salvo()
    if dispositivo_salvo is not None:
        usar = input(f"✅ Dispositivo salvo detectado ({dispositivo_salvo}). Deseja usá-lo? (S/n): ").strip().lower()
        if usar in ["", "s", "sim"]:
            index = encontrar_indice_por_nome(dispositivo_salvo)
            if verificar_sample_rate_compativel(index):
                return index
            else:
                print("❌ O dispositivo salvo não é compatível com 16000 Hz. Escolha outro.")

    dispositivos = listar_dispositivos_entrada()
    while True:
        try:
            escolha = int(input("Digite o número do dispositivo de entrada desejado: "))
            if 0 <= escolha < len(dispositivos):
                nome = dispositivos[escolha][0]
                index = encontrar_indice_por_nome(nome)
                if verificar_sample_rate_compativel(index):
                    salvar_dispositivo(nome)
                    return index
                else:
                    print("❌ Este dispositivo não é compatível com 16000 Hz. Escolha outro.")
            else:
                print("❌ Índice inválido. Tente novamente.")
        except ValueError:
            print("❌ Entrada inválida. Digite apenas números.")
