import sys
sys.path.append("core/")
sys.path.append("internal/")

import join
import chat
import left

COMMAND_DB = {
	"join":join.Join,
	"chat":chat.Chat
}

INTERNAL_DB = {
	"left":left.Left
}