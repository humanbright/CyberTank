from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import traceback
from typing import Dict, Union
import base64

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
        try:
            await websocket.send_json(data)
        except WebSocketDisconnect:
            self.disconnect(websocket)
            print(f"Client disconnected while sending personal message.")

    async def broadcast_data_dict(self, message: dict, sender: WebSocket):
        for connection in list(self.active_connections.keys()):
            if connection != sender:  # Check if the connection is not the sender
                await connection.send_json(message)
        

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
            # print(data)
            event = data["type"]
            try:
                match event:
                    case "movement":
                        await manager.broadcast_data_dict(data, websocket)
                    case "turrent":
                        await manager.broadcast_data_dict(data, websocket)
                    case "video":
                        # Pass `websocket` as the second argument to exclude the sender from the broadcast
                        await manager.broadcast_data_dict(data, websocket)

            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
                await manager.send_personal_message({"error": str(e)}, websocket)
    except WebSocketDisconnect:
        print("Disconnecting...")
        manager.disconnect(websocket)