#!/usr/bin/env python

import aiohttp
from aiohttp import web, WSCloseCode
import asyncio

#from gpiozero import CamJamKitRobot

#robot = CamJamKitRobot()


state = {
    "up": 0,
    "down": 0,
    "left": 0,
    "right": 0
}

def drive(command):
    global state
    command = message.split()
    if command[1] == "press":
        state[command[0]] += 1
    elif command[1] == "release":
        state[command[0]] -= 1
    
    left = right = 0.0
    left += - state["up"] + state["down"] + state["left"] - state["right"]
    right += - state["up"] + state["down"] + state["right"] - state["left"]

    left = min(max(left, -1), 1)
    right = min(max(right, -1), 1)
    print(left, right)
    #robot.value = (left, right)


async def http_handler(request):
    return web.FileResponse("index.html")


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            drive(msg.data)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())

    return ws


def create_runner():
    app = web.Application()
    app.add_routes([
        web.get("/", http_handler),
        web.get('/ws', websocket_handler),
    ])
    app.router.add_static("/", ".")
    return web.AppRunner(app)


async def start_server(host="127.0.0.1", port=80):
    runner = create_runner()
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    loop.run_forever()