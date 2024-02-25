import asyncio
import websockets
import json
import cv2
import numpy as np
import base64

# drivers
from Motor import Motor
from Servo import Servo

servo = Servo()
PWM = Motor()

PWM.setMotorModel(0, 0, 0, 0)

def set_rover_movement(x, y):
    """
    Sets the motor model for the rover based on x and y joystick inputs.

    :param x: The x-coordinate of the joystick, ranging from -1 to 1.
    :param y: The y-coordinate of the joystick, ranging from -1 to 1.
    """

    # Calculate motor speeds based on x and y inputs
    w = 2000 * (x + y)
    x_motor = 2000 * (x + y)
    y_motor = 2000 * (-x + y)
    z = 2000 * (-x + y)
    
    # Ensure motor speeds are within the -2000 to 2000 range
    w, x_motor, y_motor, z = map(lambda speed: max(min(speed, 2000), -2000), [w, x_motor, y_motor, z])

    # Set the motor model values
    PWM.setMotorModel(int(w), int(x_motor), int(y_motor), int(z))

async def send_frames(websocket, cam, connection_state):
    fcount = 0  # Initialize frame count
    while connection_state["is_open"]:
        # Get image from camera
        result, image = cam.read()
        if not result:
            print("Failed to capture image")
            break
        # rotate
        image = cv2.rotate(image, cv2.ROTATE_180_CLOCKWISE)
        # Compress the image to JPEG to reduce size
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 50])
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')

        try:
            await websocket.send(json.dumps({"type": "video", "data": jpg_as_text}))
            # print("sent " + str(fcount))
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
            if 'positions' in data:
                if data['type'] == 'movement':
                    positions = data['positions']
                    print(positions)
                    print(type(positions))
                    # Assuming positions is a dictionary with x and y keys
                    set_rover_movement(positions[0], positions[1])
                else:
                    # Do turrent movement here
                    y = data['positions'][1]
                    x = data['positions'][0]
                    threshold = 0.1
                    if y > threshold:
                        servo.lookUp()
                    elif y < -threshold:
                        servo.lookDown()

                    if x > threshold:
                        servo.lookRight()
                    elif x < -threshold:
                        servo.lookLeft()

    except websockets.exceptions.ConnectionClosed:
        print("Connection closed by server.")
    finally:
        connection_state["is_open"] = False

async def rover_client(uri):
    while(True):
        try:
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                print("Cannot open camera")
                return
            
            connection_state = {"is_open": True}

            try:
                async with websockets.connect(uri) as websocket:
                    # Create a task for send_frames
                    send_frames_task = asyncio.create_task(send_frames(websocket, cam, connection_state))
                    # Create a task for receive_events
                    receive_events_task = asyncio.create_task(receive_events(websocket, connection_state))
                    
                    # Wait for tasks to complete
                    await asyncio.gather(send_frames_task, receive_events_task)
                        

            except Exception as e:
                print(f"WebSocket Error: {e}")
            finally:
                cam.release()
                cv2.destroyAllWindows()
        except Exception as e:
            pass
        

uri = "wss://713745338d17.ngrok.app/ws"
# uri = "ws://127.0.0.1:8000/ws"
asyncio.run(rover_client(uri))


