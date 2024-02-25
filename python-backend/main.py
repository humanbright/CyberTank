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
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print("Client Connected!")

    def disconnect(self, client_id: str):
        del self.active_connections[client_id]
        print("Client Disconnected")

    async def send_personal_message(self, data: dict, websocket: WebSocket):
        await websocket.send_json(data)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
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
async def websocket_endpoint(websocket: WebSocket, client_id: Union[str, None] = None):
    if client_id is None:
        client_id = websocket.query_params.get("client_id")

    if client_id is None:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, client_id)

    async def update_callback(data):
        await manager.send_personal_message(data, websocket)
        
    try:
        while True:
            data = await websocket.receive_json()
            event = data["event"]
            try:
                match event:
                    # send image to unity
                    case "convert_send_image":
                        convertedImage = data["image"]
                        await manager.send_personal_message(
                            {"event": "received_image", "image": convertedImage}, websocket
                        )
                    # send unity inputs to rover
                    case "convert_unity_inputs":
                        convertedInputs = data["inputs"]
                        await manager.send_personal_message(
                            {"event": "received_input", "inputs" : convertedInputs}, websocket
                        )
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
                await manager.send_personal_message({"error": str(e)}, websocket)
    except WebSocketDisconnect:
        print("Disconnecting...")
        manager.disconnect(client_id)