import json
import asyncio
import websockets

from core.globalset import Channel
from core.join import join

channels = Channel()

async def serverrecv(websocket):
	try:
		async for message in websocket:
			try:
				message = json.loads(message)
			
			except:
				print("can't handle other data except json")

			else:
				if ("cmd" and "nick" and "channel") in message:
					if message["cmd"] == "join":
						global channels
						result = join(nick=message["nick"],
							joinchannel=message["channel"],
							channels=channels,
							websocket=websocket)
						await websocket.send(result)

	finally:
		channels.user_leave(websocket)
		print(websocket,"left")
	



async def serverrun(websocket,path):
	'''
	start running
	'''
	await serverrecv(websocket)


if __name__ == '__main__':
	server = websockets.serve(
		serverrun,
		"localhost",
		6060)
	asyncio.get_event_loop().run_until_complete(server)
	asyncio.get_event_loop().run_forever()