import sys
sys.path.append("core/")
sys.path.append("internal/")
sys.path.append("admin/")
sys.path.append("mod/")

# core
from core import *

# internal
from internal import *

# admin
from admin import *

# mod
from mod import *


COMMAND_DB = {
	"join":join.Join,
	"chat":chat.Chat,
	"emote":emote.Emote,
	"changecolor":changecolor.ChangeColor,
	"whisper":whisper.Whisper,
	"warn":warn.Warn,
	"kick":kick.Kick
	}

INTERNAL_DB = {
	"left":left.Left
	}
