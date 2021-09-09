#!/usr/bin/env python

import asyncio
import websockets

from gpiozero import CamJamKitRobot

robot = CamJamKitRobot()


state = {
    "up": 0,
    "down": 0,
    "left": 0,
    "right": 0
}

async def drive(websocket, path):
    global state, robot
    async for message in websocket:
        #print("Command: "+message)
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

        robot.value = (left, right)

async def main():
    async with websockets.serve(drive, port=2155):
        await asyncio.Future()  # run forever

asyncio.run(main())


