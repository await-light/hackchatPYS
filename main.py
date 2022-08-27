import re
import json
import time
import base64
import hashlib
import asyncio
import logging
import websockets

'''
warn: text(str),channel(str),time(number)
onlineAdd: nick(str),trip(str),channel(str),time(number)
onlineSet: nicks(list),channel(str),time(number)
onlineRemove: nick(str),trip(str or null),channel(str),time(number)
info: text(str or null),channel(str),time(number)
emote: nick(str),trip(str or null),text(str),channel(str),time(number)
chat: nick(str),trip(str or null),text(str),color(code)
	,statu(shortcode),channel(str),time(number)
'''

class User:
	def __init__(self,websocket,channel,nick,trip):
		self.websocket = websocket
		self.channel = channel
		self.nick = nick
		self.trip = trip
		self.statu = None
		self.color = "996633"
		self.level = "user"

class UserList:
	def __init__(self):
		self.userlist = set()

	def channel(self,channel):
		# return all User objects that .channel == channel
		return [user for user in self.userlist if user.channel == channel]

def chat(nick,trip,text,statu,color,level,channel):
	data = {
		"cmd":"chat",
		"nick":nick,
		"channel":channel,
		"text":text,
		"statu":statu,
		"trip":trip,
		"color":color,
		"level":level,
		"time":time.time()
		}
	return json.dumps(data)

def warn(text,channel):
	return json.dumps({
		"cmd":"warn",
		"text":text,
		"channel":channel,
		"time":time.time()
		})

def info(text,channel):
	return json.dumps({
		"cmd":"info",
		"text":text,
		"channel":channel,
		"time":time.time()
		})

def emote(nick,trip,text,channel):
	if trip == None:
		trip = "null"
	return json.dumps({
		"cmd":"emote",
		"nick":nick,
		"trip":trip,
		"text":text,
		"channel":channel,
		"time":time.time()
		})

def onlineAdd(nick,trip,channel,level):
	return json.dumps({
		"cmd":"onlineAdd",
		"nick":nick,
		"trip":trip,
		"channel":channel,
		"time":time.time()
		})

def onlineRemove(nick,trip,channel):
	return json.dumps({
		"cmd":"onlineRemove",
		"nick":nick,
		"trip":trip,
		"channel":channel,
		"time":time.time()
		})

def onlineSet(nicks,channel):
	return json.dumps({
		"cmd":"onlineSet",
		"nicks":nicks,
		"channel":channel,
		"time":time.time()
		})

async def handler_join(websocket,data,userlist):
	if "nick" not in data or "channel" not in data:
		return None

	# channel,nick,trip
	channel = data["channel"]
	try:
		nick,password = re.findall(r"^([a-zA-Z_0-9]{1,24}) ?(#.+)?$",
			data["nick"])[0]
	except:
		await websocket.send(warn(
			"Nickname must consist of up to 24 letters, " \
				"numbers, and underscores",channel))
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

	if islockall:
		with open("./data/levels.json","r") as fp:
			levels = json.load(fp)
		if trip not in levels["mod"] and trip not in levels["allowtrip"]:
			await websocket.close()
			return None

	if nick.lower() not in [u.nick.lower() for u in userlist.channel(channel)]:
		# broadcast join message to all users in the channel
		# needed: cmd,nick,trip,utype,hash,level,userid,channel,time
		user = User(websocket=websocket,channel=channel,
			nick=nick,trip=trip)
		with open("./data/levels.json","r") as fp:
			mods = json.load(fp)["mod"]
		if trip in mods:
			user.level = "mod"

		websockets.broadcast(
			[u.websocket for u in userlist.channel(channel)],
			onlineAdd(nick,trip,channel,user.level))

		userlist.userlist.add(user)

		await websocket.send(
			onlineSet([u.nick for u in userlist.channel(channel)],channel))
		await websocket.send(info("hi,welcome!",channel))

		logging.info("%s> %s-%s joined" % (channel,trip,nick))
	else:
		await websocket.send(warn("Nickname taken",channel))

async def handler_left(websocket,userlist):
	await websocket.close()
	for user in userlist.userlist:
		if user.websocket == websocket:
			user = user
			break
	else:
		return None

	websockets.broadcast([u.websocket for u in userlist.channel(user.channel)],
		onlineRemove(user.nick,user.trip,user.channel))
	userlist.userlist.remove(user)

	logging.info("%s> %s-%s left" % (user.channel,user.trip,user.nick))

async def handler_chat(websocket,data,userlist):
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

	if text.startswith("/"):
		text = text[1:].strip()
		if text == "":
			command = ["/"]
		elif not text.startswith("/"):
			command = text.split()
		else:
			command = None
	else:
		command = None
	
	global emojis
	global islockall
	
	if command != None:
		if command[0] == "help":
			await websocket.send(
				info(
					"/afk\n" \
					"/color (color code)\n" \
					"/listmods\n" \
					"/mod (add|remove) (trip)\n" \
					"/search (chars)\n" \
					"/setstatu :(emoji shortcode):\n" \
					"/shrug\n" \
					"/lockall\n" \
					"/unlockall\n" \
					"/allowtrip (add|remove) (trip)\n",False))
			return None

		elif command[0] == "shrug":
			text = r"¯\\\_(ツ)\_/¯"

		elif command[0] == "afk":
			websockets.broadcast(
				[u.websocket for u in userlist.channel(user.channel)],
				emote(user.nick,user.trip,"%s left" % user.nick,user.channel))
			return None

		elif command[0] == "search":
			if len(command) == 1:
				await websocket.send(
					info("Usage: /search (chars)",user.channel))
				return None

			searchemoji = re.findall(r"^([a-zA-Z0-9_-]+)$",command[1])
			if searchemoji != []:
				searchemoji = searchemoji[0]
				findresult = ""
				for emoji,shortcode in emojis.items():
					if searchemoji in shortcode:
						shortcode = shortcode.replace("_",r"\_")
						shortcode = shortcode.replace(searchemoji,f"=={searchemoji}==")
						findresult = findresult + f"{emoji} -> {shortcode}\n"
				if findresult == "":
					findresult = "Unable to find: %s" % searchemoji
				await websocket.send(info(findresult,user.channel))
			else:
				await websocket.send(
					warn("Emoji shortcode is made of a-z,A-Z,0-9,-,_",False))

			return None

		elif command[0] == "setstatu":
			if len(command) == 1:
				await websocket.send(
					info("Usage: /setstatu :(emoji shortcode):",user.channel))
				return None

			matchstatu = re.findall(r"^(\:[a-zA-Z0-9_-]+\:)$",command[1])
			if matchstatu != []:
				for emoji,shortcode in emojis.items():
					if shortcode == matchstatu[0]:
						user.statu = emoji
						break
				else:
					await websocket.send(
						info("Unable to find: %s" % matchstatu[0],user.channel))
			elif command[1] == "null":
				user.statu = None
			else:
				await websocket.send(
					warn("Please give correct shortcode.",user.channel))
			return None

		elif command[0] == "color":
			if len(command) == 1:
				await websocket.send(
					info("Usage: /color (color code)",user.channel))
				return None

			matchcolor = re.findall(r"^#?([A-Fa-f0-9]{6})$",command[1])
			if matchcolor != []:
				colorcode = matchcolor[0]
				user.color = colorcode
			elif command[1] == "colorful":
				user.color = "colorful"
			else:
				await websocket.send(warn("Please give correct color code.",user.channel))
			return None

		elif command[0] == "lockall":
			if user.level == "mod":
				islockall = True
				await websocket.send(info("Lockall is now open.",user.channel))
			else:
				await websocket.send(warn("You can't operate",user.channel))
			return None

		elif command[0] == "unlockall":
			if user.level == "mod":
				islockall = False
				await websocket.send(info("Lockall is now closed.",user.channel))
			else:
				await websocket.send(warn("You can't operate",user.channel))
			return None

		elif command[0] == "allowtrip":
			if user.level == "mod":
				if len(command) == 1 or len(command) == 2:
					await websocket.send(
						info("Usage: /allowtrip (add|remove) (trip)",user.channel))
					return None

				with open("./data/levels.json","r") as fp:
					levels = json.load(fp)

				if command[1] == "add":
					levels["allowtrip"].append(command[2])
					with open("./data/levels.json","w") as fp:
						json.dump(levels,fp,indent=6)
					await websocket.send(
						info("Add allowtrip %s" % command[2],user.channel))
				elif command[1] == "remove":
					levels["allowtrip"].append(command[2])
					with open("./data/levels.json","w") as fp:
						json.dump(levels,fp,indent=6)
					await websocket.send(
						info("Remove allowtrip %s" % command[2],user.channel))
				else:
					await websocket.send(warn("Error usage",user.channel))
			else:
				await websocket.send(warn("You can't operate",user.channel))

			return None

		elif command[0] == "mod":
			if user.level == "mod":
				if len(command) == 1 or len(command) == 2:
					await websocket.send(
						info("Usage: /mod (add|remove) (trip)",user.channel))
					return None

				with open("./data/levels.json","r") as fp:
					levels = json.load(fp)

				if command[1] == "add":
					levels["mod"].append(command[2])
					with open("./data/levels.json","w") as fp:
						json.dump(levels,fp,indent=6)
					await websocket.send(
						info("Add mod %s" % command[2],user.channel))
				elif command[1] == "remove":
					levels["mod"].append(command[2])
					with open("./data/levels.json","w") as fp:
						json.dump(levels,fp,indent=6)
					await websocket.send(
						info("Remove mod %s" % command[2],user.channel))
				else:
					await websocket.send(warn("Error usage",user.channel))
			else:
				await websocket.send(warn("You can't operate",user.channel))

			return None

		elif command[0] == "listmods":
			if user.level == "mod":
				with open("./data/levels.json","r") as fp:
					mods = json.load(fp)["mod"]
					await websocket.send(info(",".join(mods),user.channel))
			else:
				await websocket.send(warn("You can't operate",user.channel))
			return None

		else:
			await websocket.send(warn("Unknown command: %s" % data["text"],user.channel))
			return None

	for emoji,shortcode in emojis.items():
		text = text.replace(shortcode,emoji)

	websockets.broadcast(
		[u.websocket for u in userlist.channel(user.channel)],
		chat(user.nick,user.trip,text,user.statu,user.color,user.level,user.channel))

	logging.info("%s> %s-%s: %s" % (user.channel,user.trip,user.nick,text))

async def handler(websocket):
	global userlist
	global join

	while True:
		try:
			data = await websocket.recv()
		except:
			await handler_left(websocket,userlist)
			break

		try:
			data = json.loads(data)
		except json.decoder.JSONDecodeError:
			logging.warning("recv data not json,content: %s" % data)
			await handler_left(websocket,userlist)
			break
		else:
			if "cmd" not in data:
				continue
			else:
				cmdtype = data["cmd"]

			if cmdtype == "join":
				await handler_join(websocket,data,userlist)
			elif cmdtype == "chat":
				await handler_chat(websocket,data,userlist)

async def server_run(websocket,path):
	await handler(websocket)

if __name__ == '__main__':
	logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",level=10)
	with open("./emoji.txt","r",encoding="utf-8") as f:
		emojis = dict(re.findall(r"([^ ]+) (\:[a-zA-Z0-9_-]+\:) ?\n",f.read()))
	userlist = UserList()
	salt = b'''j\'[5:],u~$??ioveu6$?$w/jqp/^bp\\coeu8"<i"~&<+2t;i3\\:h8;-2]]z~{a.c,
	\\e-38%$ng7^+:\\5kq#d\\\\}uu|!sm7~;#!bq\'!@\'25y|>n/zxk#b8;@)!#zl.b-:~~@u{8:&g&
	"b?pj,_ibp)o+xv(8._{33d1iy#_`k5pn!jn+/#w~h~s4(=8!lo+r,gvxm&&"47604wn*df7:v52^+b
	"}n|o{cgdxf`3_l71rcd(q=7*w1re:yw&\\y$5:wao?3e/ymvb-%.^d,ta#_33zk,;"o&<|3025"h,ox
	(#"u&xrljg(6^e,sj@v|@.i5u7*z0~`t(x@a)-4&+m|+|;3,{*4\\j`<i~|=`*<w"l]}iw,2\'d/h=r8
	!-\'<xd_\\+tc%eqg.*]t;[|v?1,e:q@#.d"cc]w*"m:7~p\'>\'1$3s4|7>xc6rg`j++!@^e?!yv<b>
	~-8_l@`p(6%>%;^y:6,/kb{@we_jnhtw5yi7);~?~5>[h@/_n^3'''
	
	islockall = False

	server = websockets.serve(server_run,"0.0.0.0",6060)
	# python <= 3.10
	asyncio.get_event_loop().run_until_complete(server)
	asyncio.get_event_loop().run_forever()
