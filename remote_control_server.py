#!/usr/bin/env python

import aiohttp
from aiohttp import web, WSCloseCode
import asyncio

from gpiozero import CamJamKitRobot


# Get robot
robot = CamJamKitRobot()

# This variable counts how many users currenly are pressing each direction
state = {
    "up": 0,
    "down": 0,
    "left": 0,
    "right": 0
}

def reset_state():
    global state
    print("Reset state")
    for key in state.keys():
        state[key] = 0

def drive(command):
    global state, robot

    # Split command. First comes what direction, then if pressed or released 
    command = command.split()
    if command[1] == "press":
        # Modify global state
        state[command[0]] += 1
    elif command[1] == "release":
        state[command[0]] -= 1
    
    # Don't allow negative
    state[command[0]] = max(0, state[command[0]])
    
    # Translate state to left and right motor direction
    left = - state["up"] + state["down"] + state["left"] - state["right"]
    right = - state["up"] + state["down"] + state["right"] - state["left"]

    # Clamp between -1 and 1 (gets exception otherwise, so can't make it go faster :( ))
    left = min(max(left, -1), 1)
    right = min(max(right, -1), 1)

    robot.value = (left, right)


async def http_handler(request):
    # Serve http webpage
    return web.FileResponse("index.html")


async def websocket_handler(request):
    global state
    # Capute websocket messages
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    print("New connection")

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            drive(msg.data)
        elif msg.type == aiohttp.WSMsgType.CLOSE:
            # Reset state. This will stop the robot, but it'
            reset_state()
            print("Connection closed")
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())
            reset_state()



    return ws


def create_runner():
    # Create runner for both http-webpage and websocket handler
    app = web.Application()
    app.add_routes([
        web.get("/", http_handler),
        web.get('/ws', websocket_handler),
    ])
    app.router.add_static("/", ".")
    return web.AppRunner(app)


async def start_server(host="0.0.0.0", port=8000):
    # Start on port 8000.
    # If running through local network, it should be available to other devices. 
    # Otherwise you have to open it.
    runner = create_runner()
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    loop.run_forever()