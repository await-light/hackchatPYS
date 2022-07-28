import os
import importlib

path = "."
files = os.listdir(path)
for file in files:
	if file[-3:] == ".py" and file != "__init__.py":
		exec("%s = importlib.import_module(file[:-3])" % file[:-3])
