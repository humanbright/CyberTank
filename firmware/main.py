import asyncio
import websockets
import json
import cv2
import numpy as np
import base64

# drivers
from Motor import *
from Servo import Servo

servo = Servo()


async def send_frames(websocket, cam, connection_state):
    fcount = 0  # Initialize frame count
    while connection_state["is_open"]:
        # Get image from camera
        result, image = cam.read()
        if not result:
            print("Failed to capture image")
            break
        
        # Compress the image to JPEG to reduce size
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 50])
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')

        try:
            await websocket.send(json.dumps({"type": "video", "data": jpg_as_text}))
            print("sent " + str(fcount))
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed, stopping send_frames task.")
            break

        if cv2.waitKey(1) == ord('q'):  # Break the loop if 'q' is pressed
            break
        
        fcount += 1
        await asyncio.sleep(1/30)

async def receive_events(websocket, connection_state):
    try:
        async for message in websocket:
            data = json.loads(message)
            print("Received event:", data)
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed by server.")
    finally:
        connection_state["is_open"] = False

async def rover_client(uri):
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Cannot open camera")
        return
    
    connection_state = {"is_open": True}

    try:
        async with websockets.connect(uri) as websocket:
            send_task = asyncio.create_task(send_frames(websocket, cam, connection_state))
            receive_task = asyncio.create_task(receive_events(websocket, connection_state))
            results = await asyncio.gather(*[send_task, receive_task])
            positions = results[1]["positions"]
            threshold = 0.5
            x = positions[0]
            y = positions[1]
            if y > threshold:
                print("FORWARD")
                Forward()
            elif x > threshold:
                print("RIGHT")
                Right()
            elif y < -threshold:
                print("BACK")
                Back()
            elif x < -threshold:
                print("LEFT")
                Left()
            elif abs(x) <= threshold and abs(y) <= threshold:
                print("STOP")
                Stop()
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        cam.release()
        cv2.destroyAllWindows()

uri = "wss://713745338d17.ngrok.app/ws"
# uri = "ws://127.0.0.1:8000/ws"
asyncio.run(rover_client(uri))