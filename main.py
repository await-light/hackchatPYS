import json
import asyncio
import logging
import websockets

from core.globalset import Channel
from core.join import join

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",level=20)

channels = Channel()

async def serverrecv(websocket):
	try:
		async for message in websocket:
			try:
				message = json.loads(message)
			
			except Exception as error:
				logging.error(str(error))

			else:
				if ("cmd" and "nick" and "channel") in message:
					if message["cmd"] == "join":
						global channels
						result = join(nick=message["nick"],
							joinchannel=message["channel"],
							channels=channels,
							websocket=websocket)
						await websocket.send(result)

	except websockets.exceptions.ConnectionClosedError:
		logging.error("Connect to remote host was lost")
		pass

	finally:
		usrleft = channels.user_leave(websocket)
		if usrleft != None:
			logging.info("%s left" % usrleft)


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