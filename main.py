from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from audio.manual import escolher_dispositivo
from audio.auto import detectar_dispositivo
from audio.stream import iniciar_transcricao

import asyncio

app = FastAPI()

# Serve arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

# Lista global de conexões WebSocket
websockets = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websockets.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        pass
    finally:
        websockets.remove(websocket)

# Salva o loop principal globalmente
event_loop = asyncio.get_event_loop()

# Função que envia transcrição para todos os clientes conectados
def enviar_transcricao(texto: str):
    for ws in websockets:
        asyncio.run_coroutine_threadsafe(ws.send_text(texto), event_loop)

# Inicializa transcrição com callback no startup
@app.on_event("startup")
def startup_event():
    # Detecta o microfone automaticamente
    device_index = escolher_dispositivo()
    # device_index = detectar_dispositivo()
    iniciar_transcricao(device_index, callback=enviar_transcricao)
