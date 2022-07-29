import json
import asyncio
import logging
import websockets

import base
from commands_apply import COMMAND_DB
from commands_apply import INTERNAL_DB

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

					r = COMMAND_DB.setdefault(data["cmd"],base.empty_func)(websocket,users,data)()
					r_type = str(type(r))

					if r_type == "<class 'str'>":
						await websocket.send(r)

					elif r_type == "<class 'base.Handler'>":
						logging.info("execute %s" % r.data)
						rdatatype = str(type(r.data))

						if rdatatype == "<class 'dict'>":
							rc = COMMAND_DB.setdefault(r.data["cmd"],base.empty_func)(
								websocket,users,r.data)()
							rc_type = str(type(rc))

							if rc_type == "<class 'str'>":
								await websocket.send(rc)

						elif rdatatype == "<class 'str'>":
							await websocket.send(r.data)					


	except websockets.exceptions.ConnectionClosedError:
		# perhaps because the client disconnects without a ws.close()
		logging.error("Connect to remote host was lost")

	finally:
		data = None
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



# The Zen of Python, by Tim Peters

# Beautiful is better than ugly.
# Explicit is better than implicit.
# Simple is better than complex.
# Complex is better than complicated.
# Flat is better than nested.
# Sparse is better than dense.
# Readability counts.
# Special cases aren't special enough to break the rules.
# Although practicality beats purity.
# Errors should never pass silently.
# Unless explicitly silenced.
# In the face of ambiguity, refuse the temptation to guess.
# There should be one-- and preferably only one --obvious way to do it.
# Although that way may not be obvious at first unless you're Dutch.
# Now is better than never.
# Although never is often better than *right* now.
# If the implementation is hard to explain, it's a bad idea.
# If the implementation is easy to explain, it may be a good idea.
# Namespaces are one honking great idea -- let's do more of those!
