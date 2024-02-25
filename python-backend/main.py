import asyncio
import websockets

async def echo(websocket, path):
    # Print a message when a new connection is established
    print("New client connected")
    
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # This will run forever

asyncio.run(main())