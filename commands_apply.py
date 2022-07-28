import sys
sys.path.append("core/")
sys.path.append("internal/")

# core
import join
import chat
import color

# internal
import left

COMMAND_DB = {
	"join":join.Join,
	"chat":chat.Chat
}

INTERNAL_DB = {
	"left":left.Left
}

CALLABLE_DB = {
	"color":color.Color
}