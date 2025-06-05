# source/escolher_dispositivo.py
import sounddevice as sd
import numpy as np

def medir_volume(device_index, samplerate=16000, duration=1.0):
    try:
        recording = sd.rec(int(samplerate * duration), samplerate=samplerate,
                           channels=1, dtype='float32', device=device_index)
        sd.wait()
        audio = np.squeeze(recording)
        rms = np.sqrt(np.mean(audio**2))
        return rms
    except Exception:
        return 0.0

def detectar_dispositivo():
    dispositivos = sd.query_devices()
    entradas = [(i, d['name']) for i, d in enumerate(dispositivos) if d['max_input_channels'] > 0]

    print("🔍 Escaneando dispositivos de entrada com sinal...")
    volumes = []
    for i, nome in entradas:
        volume = medir_volume(i)
        print(f"{i}: {nome} - RMS: {volume:.6f}")
        volumes.append((volume, i, nome))

    volumes.sort(reverse=True)  # Maior volume primeiro
    volume_top, index_top, nome_top = volumes[0]

    if volume_top < 0.001:
        print("⚠️ Nenhum dispositivo com sinal detectável.")
    else:
        print(f"\n✅ Selecionado automaticamente: {index_top} - {nome_top}\n")

    return index_top
