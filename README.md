# hackchatPYS
Python server from hack.chat


## Problem
Help me check the code
There seems to be some problems


## Note
1) all commands depend on the class "base.CommandBase(websocket,base.Users,data->dict or list)".If you send commands in chat entry,the data will be like `{"arg1":...,"arg2":...}`.so if you send commands by API(like `{"cmd":"changenick","nick":"awa"}`),the data will be like just `{"cmd":"changenick","nick":"awa"}`.Remeber to add self.argslist(a list saving the args) before calling base.CommandBase if you want the command is both used text and API

2) About function's result:
	1. when get data directly:
		- if result = None,do nothing
		- if result = str (json.dumps),`await websocket.send(result)`
		- if result = base.Handler and result in commands_apply.CALLABLE_DB != None,execute specify command

	2. when making a command and ather executing it
		- if result = None,do nothing
		- if result = str (json.dumps),`await websocket.send(result)`

	TIP: only core.chat.Chat will return base.Handler object!