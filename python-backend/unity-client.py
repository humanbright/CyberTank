import asyncio
import websockets
import json
import base64

async def unity_client():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            # Listen for commands from the server
            response = await websocket.recv()
            data = json.loads(response)
            event = data.get("event")
            if event == "send_inputs":
                # get inputs
                input = "up, down, left"
                await websocket.send_json({"event": "convert_unity_inputs", "inputs": input})
            elif event == "received_image":
                # render the image
                print("image", data["image"])

asyncio.run(unity_client())