import asyncio
import websockets
import json
import cv2
import numpy as np
import base64

async def send_frames(websocket, cam):
    fcount = 0  # Initialize frame count
    while True:
        # Get image from camera
        result, image = cam.read()
        if not result:
            print("Failed to capture image")
            break
        
        # Resize the image to reduce size
        scale_percent = 50  # percent of original size
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        
        # Compress the image to JPEG to reduce size
        _, buffer = cv2.imencode('.jpg', resized)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        
        await websocket.send(json.dumps({"type": "video", "data": jpg_as_text}))
        
        print("sent " + str(fcount))
        if cv2.waitKey(1) == ord('q'):  # Break the loop if 'q' is pressed
            break
        
        fcount += 1  # Increment frame count

async def receive_events(websocket):
    async for message in websocket:
        data = json.loads(message)
        # Handle your events here
        print("Received event:", data)

async def rover_client(uri):
    # Open camera
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Cannot open camera")
        return
    
    try:
        async with websockets.connect(uri) as websocket:
            # Run sending and receiving tasks concurrently
            send_task = asyncio.create_task(send_frames(websocket, cam))
            receive_task = asyncio.create_task(receive_events(websocket))
            await asyncio.gather(send_task, receive_task)
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        cam.release()
        cv2.destroyAllWindows()

# Run the client
uri = "wss://713745338d17.ngrok.app/ws"
asyncio.run(rover_client(uri))