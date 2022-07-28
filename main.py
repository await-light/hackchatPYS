import json
import asyncio
import logging
import websockets

import base
from commands_apply import COMMAND_DB
from commands_apply import INTERNAL_DB
from commands_apply import CALLABLE_DB

# logging output config
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",level=20)

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
					'''
						if result == None
						> do nothing

						if result -> str
						> send

						if result -> handler
						> handle cmd in DB
					'''

					found = COMMAND_DB.setdefault(data["cmd"],None)

					if found != None:
						r = found(websocket,users,data)()

						if str(type(r)) == "<class 'NoneType'>":
							pass

						elif str(type(r)) == "<class 'str'>":
							await websocket.send(r)

						elif str(type(r)) == "<class 'base.Handler'>":
							execfuction = CALLABLE_DB.setdefault(r.command,None)
							if execfuction != None:
								logging.info("execute %s with %s" % (execfuction,r.args))
								rc = execfuction(websocket,users,r.args)()
								if str(type(rc)) == "<class 'str'>":
									await websocket.send(rc)
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