import asyncio
import websockets
import json
import cv2
from imageHandler import convertImage64

async def rover_client():
    client_id = "rover_client"
    uri = "ws://localhost:8000/ws?client_id={client_id}"
    
    # open camera
    cam = cv2.VideoCapture(0) 
    
    # on connect with the websocket
    async with websockets.connect(uri) as websocket:
        while True:
            # frame count to send over
            fcount = 0
            
            # get image from camera
            result, image = cam.read()
            
            # if frame count is multiple of that value send it over
            if (fcount % 1000000 == 0):
                # convert image to base 64
                convertedImage = convertImage64(image)
                await websocket.send(json.dumps({"event": "send_converted_image", "image": convertedImage}))
                   
            # Listen for commands from the server
            response = await websocket.recv()
            data = json.loads(response)
            event = data.get("event")
            
            # handles event where we need to transfer inputs to the rover
            if event == "received_input":
                # handle input / send to dylan to do
                print("inputs", data["inputs"])

# run the client
asyncio.run(rover_client())