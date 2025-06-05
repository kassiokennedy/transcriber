# Anotações

## Configurações do Windows

### 🔍 1. Capturar áudio do sistema ("o que está sendo reproduzido") no Windows

Para isso, você precisa de "Mixagem Estéreo" (Stereo Mix) ativada no Windows.

Como ativar:
Clique com o botão direito no ícone de som (🔊) na barra do Windows → Sons.

Vá na aba "Gravação".

Clique com o botão direito e ative "Mostrar dispositivos desabilitados".

Habilite "Mixagem estéreo".

import sounddevice as sd
import json
import os

CONFIG_FILE = "config.json"

def listar_dispositivos_entrada():
dispositivos = sd.query_devices()
vistos = set()
unicos = []

    for i, d in enumerate(dispositivos):
        if d['max_input_channels'] > 0:
            nome = d['name']
            if nome not in vistos:
                vistos.add(nome)
                unicos.append((i, nome))

    print("\n🎧 Dispositivos de entrada disponíveis:")
    for i, nome in unicos:
        print(f"{i}: {nome}")

    return unicos

def salvar_dispositivo(index):
with open(CONFIG_FILE, "w", encoding="utf-8") as f:
json.dump({"device_index": index}, f)

def carregar_dispositivo_salvo():
if os.path.exists(CONFIG_FILE):
try:
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
data = json.load(f)
return data.get("device_index")
except:
return None
return None

def escolher_dispositivo():
dispositivo_salvo = carregar_dispositivo_salvo()
if dispositivo_salvo is not None:
usar = input(f"✅ Dispositivo salvo detectado (#{dispositivo_salvo}). Deseja usá-lo? (S/n): ").strip().lower()
if usar in ["", "s", "sim"]:
return dispositivo_salvo

    dispositivos = listar_dispositivos_entrada()
    indices_validos = [i for i, _ in dispositivos]
    while True:
        try:
            escolha = int(input("Digite o número do dispositivo de entrada desejado: "))
            if escolha in indices_validos:
                salvar_dispositivo(escolha)
                return escolha
            else:
                print("❌ Índice inválido. Tente novamente.")
        except ValueError:
            print("❌ Entrada inválida. Digite apenas números.")

```python

```

main

```python
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
from source import escolher_dispositivo

# Configuração

sample_rate = 16000
device_index = escolher_dispositivo()

# Carrega o modelo (sem CUDA)

model = WhisperModel("base", device="cpu")

# Callback de captura de áudio

def callback(indata, frames, time, status):
if status:
print("⚠️", status)
audio = np.squeeze(indata)
segments, \_ = model.transcribe(audio, language="pt", beam_size=5)
for segment in segments:
print("🗣️", segment.text)

# Inicia stream

print("🎤 Fale algo (Ctrl+C para parar)...")
with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback, blocksize=sample_rate\*5, device=device_index):
while True:
sd.sleep(500)

```
