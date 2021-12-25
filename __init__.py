import sys
import importlib
from collections import namedtuple
Dependency = namedtuple("Dependency", ["module", "package", "name"])

bl_info = {
	"name": "Clean Graph",
	"author": "S.M.Hossein Fatemi",
	"version": (1, 0),
	"blender": (2, 93, 0),
	"category": "Animation",
	"location": "graph editor",
	"description": "Tries to clean your dense mocap graph like an animator would!",
}

dependencies = (Dependency(module="scipy", package=None, name=None),)
modulesNames = ['clean_graph_utils', 'clean_graph_op', 'clean_graph_ui', 'install_dependencies']

modulesFullNames = {}
for currentModuleName in modulesNames:
	modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))

for currentModuleFullName in modulesFullNames.values():
	if currentModuleFullName in sys.modules:
		importlib.reload(sys.modules[currentModuleFullName])
	else:
		globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
		setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)
 
def register():
	for currentModuleName in modulesFullNames.values():
		if currentModuleName in sys.modules:
			if hasattr(sys.modules[currentModuleName], 'register'):
				sys.modules[currentModuleName].register()

def unregister():
	for currentModuleName in modulesFullNames.values():
		if currentModuleName in sys.modules:
			if hasattr(sys.modules[currentModuleName], 'unregister'):
				sys.modules[currentModuleName].unregister()

if __name__ == "__main__":
	register()

