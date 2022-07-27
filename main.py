import json
import asyncio
import logging
import websockets

from base import Users
from commands_apply import COMMAND_DB

# logging output config
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",level=10)

# all user objects
users = Users()

async def server_recv(websocket):
	try:
		async for data in websocket:
			try:
				data = json.loads(data)
			
			except Exception as error:
				logging.error(str(error))

			else:
				websocket = websocket
				global users
				users = users
				data = data

				if "cmd" in data:
					findresult = COMMAND_DB.setdefault(data["cmd"],None)
					if findresult != None:
						r = findresult(websocket,users,data)()
						await websocket.send(r)
					else:
						logging.warning("Command Not Found :%s" % data["cmd"])

	except websockets.exceptions.ConnectionClosedError:
		# perhaps because the client disconnects without a ws.close()
		logging.error("Connect to remote host was lost")

	finally:
		pass


async def server_run(websocket,path):
	'''
	start running
	'''
	await server_recv(websocket)


if __name__ == '__main__':
	server = websockets.serve(
		server_run,
		"localhost",
		6060)
	asyncio.get_event_loop().run_until_complete(server)
	asyncio.get_event_loop().run_forever()