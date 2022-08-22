import re
import json
import time
import crypt
import base64
import hashlib
import asyncio
import logging
import websockets

# logging output config
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",level=10)

class User:
	def __init__(self,websocket,channel,nick,trip):
		self.websocket = websocket
		self.channel = channel
		self.nick = nick
		self.trip = trip

class UserList:
	def __init__(self):
		self.userlist = set()

	def channel(self,channel):
		# return all User objects that .channel == channel
		return [user for user in self.userlist if user.channel == channel]

userlist = UserList()
salt = b'''j\'[5:],u~$??ioveu6$?$w/jqp/^bp\\coeu8"<i"~&<+2t;i3\\:h8;-2]]z~{a.c,
\\e-38%$ng7^+:\\5kq#d\\\\}uu|!sm7~;#!bq\'!@\'25y|>n/zxk#b8;@)!#zl.b-:~~@u{8:&g&
"b?pj,_ibp)o+xv(8._{33d1iy#_`k5pn!jn+/#w~h~s4(=8!lo+r,gvxm&&"47604wn*df7:v52^+b
"}n|o{cgdxf`3_l71rcd(q=7*w1r:yw&\\y$5:wao?3e/ymvb-%.^d,ta#_33zk,;"o&<|3025"h,ox
(#"u&xrljg(6^e,sj@v|@.i5u7*z0~`t(x@a)-4&+m|+|;3,{*4\\j`<i~|=`*<w"l]}iw,2\'d/h=r8
!-\'<xd_\\+tc%eqg.*]t;[|v?1,e:q@#.d"cc]w*"m:7~p\'>\'1$3s4|7>xc6rg`j++!@^e?!yv<b>
~-8_l@`p(6%>%;^y:6,/kb{@we_jnhtw5yi7);~?~5>[h@/_n^3'''

async def join(websocket,data,userlist):
	if "nick" not in data or "channel" not in data:
		return None

	# channel,nick,trip
	channel = data["channel"]
	try:
		nick,password = re.findall(r"^([a-zA-Z_]{1,24}) ?(#.+)?$",
			data["nick"])[0]
	except:
		await websocket.send(json.dumps({
			"cmd":"warn",
			"text":"Nickname must consist of up to 24 letters, " \
				"numbers, and underscores",
			"channel":False,
			"time":time.time()} ))
		return None

	if password != "":
		password = password[1:]
		sha256obj = hashlib.sha256(salt)
		sha256obj.update(salt)
		sha256obj.update(password.encode())
		trip = sha256obj.digest()
		trip = base64.b64encode(trip).decode()[:6]
	else:
		trip = None

	if nick.lower() not in [u.nick.lower() for u in userlist.channel(channel)]:
		# broadcast join message to all users in the channel
		# needed: cmd,nick,trip,utype,hash,level,userid,channel,time
		websockets.broadcast(
			[u.websocket for u in userlist.channel(channel)],
			json.dumps({"cmd":"onlineAdd",
				"nick":nick,
				"trip":trip,
				"channel":channel}))

		userlist.userlist.add(User(websocket=websocket,channel=channel,
			nick=nick,trip=trip))
		logging.info("%s-%s joined ?%s" % (trip,nick,channel))
		await websocket.send(
			json.dumps({"cmd":"onlineSet",
				"nicks":[u.nick for u in userlist.channel(channel)],
				"channel":channel,
				"time":time.time()
				})
			)
		await websocket.send(
			json.dumps({
				"cmd":"info",
				"text":"hi,welcome!",
				"channel":channel,
				"time":time.time()
				}))
	else:
		await websocket.send(
			json.dumps({
				"cmd":"warn",
				"text":"Nickname taken",
				"channel":False,
				"time":time.time()
				}))

async def left(websocket,userlist):
	for user in userlist.userlist:
		if user.websocket == websocket:
			user = user
			break
	else:
		return None

	websockets.broadcast(
		[u.websocket for u in userlist.channel(user.channel)],
		json.dumps({
			"cmd":"onlineRemove",
			"nick":user.nick,
			"channel":user.channel,
			"time":time.time()
			}))

	userlist.userlist.remove(user)

async def chat(websocket,data,userlist):
	for user in userlist.userlist:
		if user.websocket == websocket:
			user = user
			break
	else:
		return None

	if "text" not in data:
		return None
	else:
		text = data["text"]

	if text[0] == "/":
		text = text[1:]

		if text == "shrug":
			text = r"¯\\\_(ツ)\_/¯"
		elif text == "cry":
			text = r"T^T"
		else:
			await websocket.send(
				json.dumps({
					"cmd":"warn",
					"text":"Unknown command: /%s" % text,
					"channel":False,
					"time":time.time()
					}))
			return None

	websockets.broadcast(
		[u.websocket for u in userlist.channel(user.channel)],
		json.dumps({
			"cmd":"chat",
			"nick":user.nick,
			"channel":user.channel,
			"text":text,
			"trip":user.trip,
			"time":time.time()
			}))

async def handler(websocket):
	global userlist
	global join

	while True:
		try:
			data = await websocket.recv()
		except:
			await left(websocket,userlist)
			break

		try:
			data = json.loads(data)
		except json.decoder.JSONDecodeError:
			logging.warning("recv data not json,content: %s" % data)
			continue
		else:
			if "cmd" not in data:
				continue
			else:
				cmdtype = data["cmd"]

			if cmdtype == "join":
				await join(websocket,data,userlist)
			elif cmdtype == "chat":
				await chat(websocket,data,userlist)

async def server_run(websocket,path):
	await handler(websocket)

if __name__ == '__main__':
	server = websockets.serve(server_run,"0.0.0.0",6060)
	# python <= 3.10
	asyncio.get_event_loop().run_until_complete(server)
	asyncio.get_event_loop().run_forever()
