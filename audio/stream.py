# mode/stream.py
import sounddevice as sd
import numpy as np
import resampy
from faster_whisper import WhisperModel
import threading, queue

DESIRED_SR = 16000
BUFFER_DURATION = 5.0  
MIN_RMS = 1e-3 

audio_queue = queue.Queue()

def carregar_modelo():
    return WhisperModel("small", device="cpu", compute_type="int8")
    # return WhisperModel("small", device="cpu", compute_type="int8_float16")

def processador(modelo, callback=None):
    while True:
        audio = audio_queue.get()
        if audio is None:
            break
        segments, _ = modelo.transcribe(audio, language="pt", vad_filter=True, beam_size=1)
        for segment in segments:
            texto = segment.text.strip()
            if texto:
                print("🗣️", texto)
                if callback:
                    callback(texto)


def iniciar_transcricao(device_index, callback=None, modelo=None):
    if modelo is None:
        modelo = carregar_modelo()

    device_info = sd.query_devices(device_index, "input")
    native_sr = int(device_info['default_samplerate'])

    if native_sr != DESIRED_SR:
        print(f"⚠️ O dispositivo usa {native_sr} Hz, reamostrando para {DESIRED_SR} Hz.")

    transcricao_thread = threading.Thread(target=processador, args=(modelo, callback), daemon=True)
    transcricao_thread.start()

    buffer = np.empty((0,), dtype=np.float32)
    total_duration = 0.0

    def callback_audio(indata, frames, time, status):
        nonlocal buffer, total_duration
        if status:
            print(" ⚠️ ", status)

        audio = np.squeeze(indata)
        if np.sqrt(np.mean(audio**2)) < MIN_RMS:
            return  # ignora silêncio

        buffer = np.concatenate((buffer, audio))
        total_duration = len(buffer) / native_sr

        if total_duration >= BUFFER_DURATION:
            audio_to_send = buffer.copy()

            if native_sr != DESIRED_SR:
                audio_to_send = resampy.resample(audio_to_send, native_sr, DESIRED_SR)

            audio_queue.put(audio_to_send)
            buffer = np.empty((0,), dtype=np.float32)
            total_duration = 0.0

    def escuta():
        print("\n🎤 Fale algo (Ctrl+C para parar)...\n")
        with sd.InputStream(samplerate=native_sr, channels=1, callback=callback_audio, device=device_index):
            while True:
                sd.sleep(250)

    # Rodar escuta em thread separada
    escuta_thread = threading.Thread(target=escuta, daemon=True)
    escuta_thread.start()

