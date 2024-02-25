from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import traceback
from typing import Dict, Union

# from imageHandler import convertImage64, convertImageNp

# example json from rover?:
# {
#   "event": "convert_send_image",
#   "image": ".jpg , .png"
# }

# example json from uniqty?:
# {
#   "event": "",
#   "inputs": {}?
# }

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = "Anonymous"  # Or use some unique identifier of your choice
        print("Client Connected!")

    def disconnect(self, websocket: WebSocket):
        del self.active_connections[websocket]
        print("Client Disconnected")

    async def send_personal_message(self, data: dict, websocket: WebSocket):
        if websocket in self.active_connections:
            await websocket.send_json(data)

    async def broadcast(self, message: str):
        for connection in self.active_connections.keys():
            await connection.send_text(message)


manager = ConnectionManager()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to more restrictive origins as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return "backend server"


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
        
    try:
        while True:
            data = await websocket.receive_json()
            event = data["type"]
            try:
                match event:
                    # send image to unity
                    case "send_converted_image":
                        convertedImage = data["image"]
                        await manager.send_personal_message(
                            {"event": "received_image", "image": convertedImage}, websocket
                        )
                    # send unity inputs to rover
                    case "send_unity_inputs":
                        convertedInputs = data["inputs"]
                        await manager.send_personal_message(
                            {"event": "received_input", "inputs" : convertedInputs}, websocket
                        )
                    case "movement":
                        print(data['positions'])
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
                await manager.send_personal_message({"error": str(e)}, websocket)
    except WebSocketDisconnect:
        print("Disconnecting...")
        manager.disconnect(websocket)