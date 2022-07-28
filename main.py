import json
import asyncio
import logging
import websockets

import base
from commands_apply import COMMAND_DB
from commands_apply import INTERNAL_DB

# logging output config
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",level=10)

# all user objects
users = base.Users()

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

					'''
					if result == None
					> do nothing

					if result -> json
					> send

					if result -> handler
					> handle cmd in DB
					'''

					# if the cmd function in DB,execute it otherwise warning
					if findresult != None:
						r = findresult(websocket,users,data)()
						logging.debug(r)
						if r != None:
							await websocket.send(r)
					else:
						logging.warning("Command Not Found :%s" % data["cmd"])

	except websockets.exceptions.ConnectionClosedError:
		# perhaps because the client disconnects without a ws.close()
		logging.error("Connect to remote host was lost")

	finally:
		INTERNAL_DB["left"](websocket,users,data)()


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