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
            print(positions)
            print(type(positions))
            set_rover_movement(positions[0], positions[1])

    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        cam.release()
        cv2.destroyAllWindows()

uri = "wss://713745338d17.ngrok.app/ws"
# uri = "ws://127.0.0.1:8000/ws"
asyncio.run(rover_client(uri))

def set_rover_movement(x, y):
    """
    Sets the motor model for the rover based on x and y joystick inputs.

    :param x: The x-coordinate of the joystick, ranging from -1 to 1.
    :param y: The y-coordinate of the joystick, ranging from -1 to 1.
    """

    # Define the maximum speed for forward and backward movement
    max_speed = 2000
    # Define the speed for turning
    turn_speed = 500

    # Interpolate the y input for forward/backward speed
    forward_back_speed = int(y * max_speed)
    
    # Interpolate the x input for turning speed
    turn_value = int(x * turn_speed)

    # Calculate the motor speeds
    left_motor_speed = forward_back_speed - turn_value
    right_motor_speed = forward_back_speed + turn_value

    # Ensure the motor speeds are within the valid range
    left_motor_speed = max(min(left_motor_speed, max_speed), -max_speed)
    right_motor_speed = max(min(right_motor_speed, max_speed), -max_speed)

    # Set the motor model values
    PWM.setMotorModel(left_motor_speed, left_motor_speed, right_motor_speed, right_motor_speed)
