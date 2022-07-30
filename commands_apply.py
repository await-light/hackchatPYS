import sys
sys.path.append("core/")
sys.path.append("internal/")
sys.path.append("admin/")

# core
from core import *

# internal
from internal import *

# admin
from admin import *


COMMAND_DB = {
	"join":join.Join,
	"chat":chat.Chat,
	"emote":emote.Emote,
	"changecolor":changecolor.ChangeColor,
	"whisper":whisper.Whisper,
	"warn":warn.Warn
	}

INTERNAL_DB = {
	"left":left.Left
	}
