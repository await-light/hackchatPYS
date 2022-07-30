# hackchatPYS
Python server from hack.chat

## Example Website
http://124.223.190.218:6059/

## Note

### About adding new command

1. Think about the type of your command,it can be core,admin...

2. Create a new file named "<command's name>" in core or admin folder

3. You can write the basic code in it
```python
import sys
sys.path.append("../")
import base

class <CommandName>(base.CommandBase):
	def __init__(self,websocket,users,data):
		base.CommandBase.__init__(self,
			websocket=websocket,
			users=users,
			data=data)

	def execute(self):
		pass
```

4. You can find it depends on a class named `base.CommandBase(self,websocket,users,data,level=None)`,the `websocket` is the client's websocket.User object has this property `user.websocket`.The `users` is `base.Users`.The `data` is data client sent(like {"cmd":"join","nick":...,...}).Also there is a property named `level`,if its value is a number it will only allow the user has level larger than it to run this command.Usually its value is `None`,it means anyone can run it.More information please look at `base.levels`

5. Write code.Write your code in function execute,and `return result` or `broadcast`
	(1) About return result
		- NoneType
			nothing will happen
		- str <- json.dumps()
			send to the websocket

	(2) About broadcast
		send the message to everyone in specify channel
		Grammer:`self.users.broadcasttext(channel,data)`
		- channel is a string (like "lounge","your-channel")
		- data is a string <- json.dumps()

6. Add the path to python file `commands_apply.py`,add one element to `COMMAND_DB`-> "command's name":"<file>.<ClassName>"

7. If you hope your command can be used in both `text` and `API`,edit in python file `base.Handler._handledata(command,content)`.
	For example: you sent `/whisper @L hello world` in entry,
	it will call base.Handler.\_handledata(command="whisper",content="@L hello world")
	About `base.Handler._handledata(command,content)`'s result:
		- Nonetype
			nothing happen
		- str <- json.dumps()
			send to the websocket too
		- dict
			handle as json data
			For example:
			If you return `{"cmd":"changecolor","color":"FF6000"}`
			It points `core.changecolor.ChangeColor`,it is found in `commands_apply.COMMAND_DB`