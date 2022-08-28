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
		self.ip = self.websocket.remote_address[0]
		self.channel = channel
		self.nick = nick
		self.trip = trip
		self.statu = None
		self.color = "996633"
		self.level = "user"

class UserList:
	def __init__(self):
		self.userlist = set()

	def channel(self,channel,filterflag=None):
		# return all User objects that .channel == channel
		if filterflag == None:
			return [user for user in self.userlist if user.channel == channel]
		elif filterflag == "mod":
			return [user for user in self.userlist if user.channel == channel and user.level == "mod"]

	@property
	def mods(self):
		return [user for user in self.userlist if user.level == "mod"]

def chat(nick,trip,text,statu,color,level,channel):
	data = {
		"cmd":"chat",
		"nick":nick,
		"channel":channel,
		"text":text,
		"statu":statu,
		"trip":trip,
		"color":color,
		"level":level
		}
	return json.dumps(data)

def warn(text):
	return json.dumps({
		"cmd":"warn",
		"text":text
		})

def info(text):
	return json.dumps({
		"cmd":"info",
		"text":text
		})

def emote(nick,trip,text):
	if trip == None:
		trip = "null"
	return json.dumps({
		"cmd":"emote",
		"nick":nick,
		"trip":trip,
		"text":text
		})

def onlineAdd(nick,trip,level):
	return json.dumps({
		"cmd":"onlineAdd",
		"nick":nick,
		"trip":trip
		})

def onlineRemove(nick,trip):
	return json.dumps({
		"cmd":"onlineRemove",
		"nick":nick,
		"trip":trip
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
				"numbers, and underscores"))
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

	if websocket not in [u.websocket for u in userlist.userlist]:
		if nick.lower() not in [u.nick.lower() for u in userlist.channel(channel)]:
			# broadcast join message to all users in the channel
			# needed: cmd,nick,trip,utype,hash,level,userid,channel,time
			user = User(websocket=websocket,channel=channel,
				nick=nick,trip=trip)
			with open("./data/levels.json","r") as fp:
				levels = json.load(fp)
			if trip in levels["mod"]:
				user.level = "mod"
			if trip not in levels["mod"] and trip not in levels["allowtrip"]:
				if user.ip in ban_list:
					await websocket.send(warn("No way~"))
					await websocket.close()
					return None
				if channel in lockroom_list:
					await websocket.send(warn("Now locked."))
					await websocket.close()
					return None

			websockets.broadcast(
				[u.websocket for u in userlist.channel(channel)],
				onlineAdd(nick,trip,user.level))

			userlist.userlist.add(user)

			await websocket.send(
				onlineSet([u.nick for u in userlist.channel(channel)],channel))
			await websocket.send(info("hi,welcome!"))

			logging.info("%s> %s:%s-%s-%s joined" % (channel,websocket.host,websocket.port,trip,nick))
		else:
			await websocket.send(warn("Nickname taken"))
	else:
		await websocket.send(warn("You can't join more than one channel."))

async def handler_left(websocket,userlist):
	await websocket.close()
	for user in userlist.userlist:
		if user.websocket == websocket:
			user = user
			break
	else:
		return None

	websockets.broadcast([u.websocket for u in userlist.channel(user.channel)],
		onlineRemove(user.nick,user.trip))
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
	global lockroom_list
	global ban_list
	
	if command != None:
		if command[0] == "help":
			await websocket.send(
				info(
					"/afk\n" \
					"/shrug\n" \
					"/search (chars)\n" \
					"/color (color code)\n" \
					"/setstatu|ss :(emoji shortcode):\n" \
					"**/allowtrip (add|remove) (trip)**\n" \
					"**/listallowtrips**\n" \
					"**/mod (add|remove) (trip)**\n" \
					"**/listmods**\n" \
					"**/lockroom**\n" \
					"**/unlockroom**\n" \
					"**/lockall**\n" \
					"**/unlockall**\n" \
					"**/kick (nick)**\n" \
					"**/ban (nick)**\n" \
					"**/unban**"))
			return None

		elif command[0] == "shrug":
			text = r"¯\\\_(ツ)\_/¯"

		elif command[0] == "afk":
			websockets.broadcast(
				[u.websocket for u in userlist.channel(user.channel)],
				emote(user.nick,user.trip,"%s left" % user.nick))
			return None

		elif command[0] == "search": # bug: replace ***searchemoji ==***searchemoji==
			if len(command) == 1:
				await websocket.send(
					info("Usage: /search (chars)"))
				return None

			searchemoji = re.findall(r"^([a-zA-Z0-9_-]+)$",command[1])
			if searchemoji != []:
				searchemoji = searchemoji[0]
				findresult = ""
				for emoji,shortcode in emojis.items():
					if searchemoji in shortcode:
						shortcode = shortcode.replace("_",r"\_")
						shortcode = shortcode.replace(searchemoji,f"=={searchemoji}==")
						findresult = findresult + f"{emoji} {shortcode}\n"
				if findresult == "":
					findresult = "Unable to find: %s" % searchemoji
				await websocket.send(info(findresult))
			else:
				await websocket.send(warn("Emoji shortcode is made of a-z,A-Z,0-9,-,_"))

			return None

		elif command[0] == "setstatu" or command[0] == "ss":
			if len(command) == 1:
				await websocket.send(
					info("Usage: /setstatu|ss :(emoji shortcode):"))
				return None

			matchstatu = re.findall(r"^(\:[a-zA-Z0-9_-]+\:)$",command[1])
			if matchstatu != []:
				for emoji,shortcode in emojis.items():
					if shortcode == matchstatu[0]:
						user.statu = emoji
						break
				else:
					await websocket.send(
						info("Unable to find: %s" % matchstatu[0]))
			elif command[1] == "null":
				user.statu = None
			else:
				await websocket.send(
					warn("Please give correct shortcode."))
			return None

		elif command[0] == "color":
			if len(command) == 1:
				await websocket.send(
					info("Usage: /color (color code)"))
				return None

			matchcolor = re.findall(r"^#?([A-Fa-f0-9]{6})$",command[1])
			if matchcolor != []:
				colorcode = matchcolor[0]
				user.color = colorcode
			elif command[1] == "colorful":
				user.color = "colorful"
			else:
				await websocket.send(warn("Please give correct color code."))
			return None

		elif command[0] == "lockall" and user.level == "mod":
			islockall = True
			websockets.broadcast(
				[u.websocket for u in userlist.mods],
				info("Lockall is now open. By:%s" % user.nick))
			return None

		elif command[0] == "unlockall" and user.level == "mod":
			islockall = False
			websockets.broadcast(
				[u.websocket for u in userlist.mods],
				(info("Lockall is now closed. By:%s" % user.nick)))
			return None

		elif command[0] == "allowtrip" and user.level == "mod":
			if len(command) == 1 or len(command) == 2:
				await websocket.send(
					info("Usage: /allowtrip (add|remove) (trip)"))
				return None

			with open("./data/levels.json","r") as fp:
				levels = json.load(fp)

			if command[1] == "add":
				levels["allowtrip"].append(command[2])
				with open("./data/levels.json","w") as fp:
					json.dump(levels,fp,indent=6)
				websockets.broadcast(
					[u.websocket for u in userlist.channel(user.channel,filterflag="mod")],
					info("Add allowtrip %s. By:%s" % (command[2],user.nick)))

			elif command[1] == "remove":
				if command[2] in levels["allowtrip"]:
					levels["allowtrip"].remove(command[2])
				with open("./data/levels.json","w") as fp:
					json.dump(levels,fp,indent=6)
				websockets.broadcast(
					[u.websocket for u in userlist.channel(user.channel,filterflag="mod")],
					info("Remove allowtrip %s. By:%s" % (command[2],user.nick)))

			else:
				await websocket.send(warn("Error usage"))

			return None

		elif command[0] == "mod" and user.level == "mod":
			if len(command) == 1 or len(command) == 2:
				await websocket.send(
					info("Usage: /mod (add|remove) (trip)"))
				return None

			with open("./data/levels.json","r") as fp:
				levels = json.load(fp)

			if command[1] == "add":
				levels["mod"].append(command[2])
				with open("./data/levels.json","w") as fp:
					json.dump(levels,fp,indent=6)
				websockets.broadcast(
					[u.websocket for u in userlist.channel(user.channel,filterflag="mod")],
					(info("Add mod %s. By %s" % (command[2],user.nick))))
			elif command[1] == "remove":
				if command[2] in levels["mod"]:
					levels["mod"].remove(command[2])
				with open("./data/levels.json","w") as fp:
					json.dump(levels,fp,indent=6)
				websockets.broadcast(
					[u.websocket for u in userlist.channel(user.channel,filterflag="mod")],
					(info("Remove mod %s. By %s" % (command[2],user.nick))))
			else:
				await websocket.send(warn("Error usage"))

			return None

		elif command[0] == "listmods" and user.level == "mod":
			with open("./data/levels.json","r") as fp:
				mods = json.load(fp)["mod"]
				await websocket.send(info("Mods:"+",".join(mods)))
			return None

		elif command[0] == "listallowtrips" and user.level == "mod":
			with open("./data/levels.json","r") as fp:
				mods = json.load(fp)["allowtrip"]
				await websocket.send(info("Allowtrips:"+",".join(mods)))
			return None

		elif command[0] == "kick" and user.level == "mod":
			if len(command) == 1:
				await websocket.send(
					info("Usage: /kick (nick)"))
				return None

			for u in userlist.channel(user.channel):
				if u.nick == command[1]:
					await u.websocket.close()
					websockets.broadcast(
						[u.websocket for u in userlist.channel(user.channel,filterflag="mod")],
						(info("Kick %s. By %s" % (command[1],user.nick))))
					break
			else:
				await websocket.send(warn("Could not find this user"))
			return None

		elif command[0] == "ban" and user.level == "mod":
			if len(command) == 1:
				await websocket.send(
					info("Usage: /ban (nick)"))
				return None

			for u in userlist.channel(user.channel):
				if u.nick == command[1]:
					ban_list.append(u.ip)
					await u.websocket.close()
					websockets.broadcast(
						[u.websocket for u in userlist.channel(user.channel,filterflag="mod")],
						(info("Ban %s. By %s" % (command[1],user.nick))))
					break
			else:
				await websocket.send(warn("Could not find this user"))
			return None

		elif command[0] == "unban" and user.level == "mod":
			ban_list = []
			websockets.broadcast(
				[u.websocket for u in userlist.channel(user.channel,filterflag="mod")],
				(info("Unban all. By %s" % user.nick)))
			return None

		elif command[0] == "lockroom" and user.level == "mod":
			if user.channel not in lockroom_list:
				lockroom_list.append(user.channel)
				websockets.broadcast(
				[u.websocket for u in userlist.channel(user.channel,filterflag="mod")],
				(info("Room is now locked. By %s" % user.nick)))
			else:
				await websocket.send(info("Already locked."))
			return None

		elif command[0] == "unlockroom" and user.level == "mod":
			if user.channel in lockroom_list:
				lockroom_list.remove(user.channel)
				websockets.broadcast(
					[u.websocket for u in userlist.channel(user.channel,filterflag="mod")],
					(info("Room is now unlocked. By %s" % user.nick)))
			else:
				await websocket.send(info("Already unlocked."))
			return None

		else:
			await websocket.send(warn("Unknown command: %s" % data["text"]))
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
		except OSError:
			continue
		except:
			await handler_left(websocket,userlist)
			break

		# OSError: [WinError 121]

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
	lockroom_list = []
	ban_list = []

	server = websockets.serve(server_run,"0.0.0.0",6060)
	# python <= 3.10
	asyncio.get_event_loop().run_until_complete(server)
	asyncio.get_event_loop().run_forever()
