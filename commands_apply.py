import sys
sys.path.append("core/")
sys.path.append("spec/")

import core
import spec

COMMAND_DB = {
	"join":core.join.Join
}

SPEC_DB = {
	"left":spec.left.Left
}