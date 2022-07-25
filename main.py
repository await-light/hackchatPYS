import json
import asyncio
import websockets

from core.globalset import Channel
from core.join import join

channels = Channel()

async def pro(websocket):
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

						print(channels.allchannel)

	except:
		pass


async def main():
	async with websockets.serve(
		pro,"localhost",6060):
		await asyncio.Future()



if __name__ == '__main__':
	asyncio.run(main())