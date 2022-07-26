import json
from websocket import create_connection

def makedata(**kwargs):
	return json.dumps(kwargs)

address = r"ws://localhost:6060/"
nicks = ["light","light ","light#","light#awa","light #awa"]

join_data = makedata(
	cmd="join",
	nick=nicks[1],
	channel="your-channel")

connection = create_connection(address)
connection.send(join_data)

try:
	while True:
		print(connection.recv())
except:
	connection.close()