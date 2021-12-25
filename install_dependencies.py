import bpy
import os
import sys
import subprocess
import importlib
from . import clean_graph_op, clean_graph_ui, bl_info, dependencies
dependent_classes = (clean_graph_op, clean_graph_ui)

def import_module(module_name, global_name=None, reload=True):
	"""
	Import a module.
	:param module_name: Module to import.
	:param global_name: (Optional) Name under which the module is imported. If None the module_name will be used.
	   This allows to import under a different name with the same effect as e.g. "import numpy as np" where "np" is
	   the global_name under which the module can be accessed.
	:raises: ImportError and ModuleNotFoundError
	"""
	if global_name is None:
		global_name = module_name

	if global_name in globals():
		importlib.reload(globals()[global_name])
	else:
		# Attempt to import the module and assign it to globals dictionary. This allow to access the module under
		# the given name, just like the regular import would.
		globals()[global_name] = importlib.import_module(module_name)

def install_pip():
	"""
	Installs pip if not already present. Please note that ensurepip.bootstrap() also calls pip, which adds the
	environment variable PIP_REQ_TRACKER. After ensurepip.bootstrap() finishes execution, the directory doesn't exist
	anymore. However, when subprocess is used to call pip, in order to install a package, the environment variables
	still contain PIP_REQ_TRACKER with the now nonexistent path. This is a problem since pip checks if PIP_REQ_TRACKER
	is set and if it is, attempts to use it as temp directory. This would result in an error because the
	directory can't be found. Therefore, PIP_REQ_TRACKER needs to be removed from environment variables.
	:return:
	"""

	try:
		# Check if pip is already installed
		subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
	except subprocess.CalledProcessError:
		import ensurepip
		ensurepip.bootstrap()
		os.environ.pop("PIP_REQ_TRACKER", None)

def install_and_import_module(module_name, package_name=None, global_name=None):
	"""
	Installs the package through pip and attempts to import the installed module.
	:param module_name: Module to import.
	:param package_name: (Optional) Name of the package that needs to be installed. If None it is assumed to be equal
	   to the module_name.
	:param global_name: (Optional) Name under which the module is imported. If None the module_name will be used.
	   This allows to import under a different name with the same effect as e.g. "import numpy as np" where "np" is
	   the global_name under which the module can be accessed.
	:raises: subprocess.CalledProcessError and ImportError
	"""
	if package_name is None:
		package_name = module_name

	if global_name is None:
		global_name = module_name

	# Blender disables the loading of user site-packages by default. However, pip will still check them to determine
	# if a dependency is already installed. This can cause problems if the packages is installed in the user
	# site-packages and pip deems the requirement satisfied, but Blender cannot import the package from the user
	# site-packages. Hence, the environment variable PYTHONNOUSERSITE is set to disallow pip from checking the user
	# site-packages. If the package is not already installed for Blender's Python interpreter, it will then try to.
	# The paths used by pip can be checked with `subprocess.run([bpy.app.binary_path_python, "-m", "site"], check=True)`

	# Create a copy of the environment variables and modify them for the subprocess call
	environ_copy = dict(os.environ)
	environ_copy["PYTHONNOUSERSITE"] = "1"

	subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True, env=environ_copy)

	# The installation succeeded, attempt to import the module again
	import_module(module_name, global_name)


# class EXAMPLE_OT_dummy_operator(bpy.types.Operator):
# 	bl_idname = "example.dummy_operator"
# 	bl_label = "Dummy Operator"
# 	bl_description = "This operator tries to use matplotlib."
# 	bl_options = {"REGISTER"}

# 	def execute(self, context):
# 		print(matplotlib.get_backend())
# 		return {"FINISHED"}


# class EXAMPLE_PT_panel(bpy.types.Panel):
# 	bl_label = "Example Panel"
# 	bl_category = "Example Tab"
# 	bl_space_type = "VIEW_3D"
# 	bl_region_type = "UI"

# 	def draw(self, context):
# 		layout = self.layout

# 		for dependency in dependencies:
# 			if dependency.name is None and hasattr(globals()[dependency.module], "__version__"):
# 				layout.label(text=f"{dependency.module} {globals()[dependency.module].__version__}")
# 			elif hasattr(globals()[dependency.name], "__version__"):
# 				layout.label(text=f"{dependency.module} {globals()[dependency.name].__version__}")
# 			else:
# 				layout.label(text=f"{dependency.module}")

# 		layout.operator(EXAMPLE_OT_dummy_operator.bl_idname)


class EXAMPLE_PT_warning_panel(bpy.types.Panel):
	bl_label = "Example Warning"
	bl_category = "Example Tab"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"

	@classmethod
	def poll(self, context):
		return not dependencies_installed

	def draw(self, context):
		layout = self.layout

		lines = [f"Please install the missing dependencies for the \"{bl_info.get('name')}\" add-on.",
				 f"1. Open the preferences (Edit > Preferences > Add-ons).",
				 f"2. Search for the \"{bl_info.get('name')}\" add-on.",
				 f"3. Open the details section of the add-on.",
				 f"4. Click on the \"{EXAMPLE_OT_install_dependencies.bl_label}\" button.",
				 f"   This will download and install the missing Python packages, if Blender has the required",
				 f"   permissions.",
				 f"If you're attempting to run the add-on from the text editor, you won't see the options described",
				 f"above. Please install the add-on properly through the preferences.",
				 f"1. Open the add-on preferences (Edit > Preferences > Add-ons).",
				 f"2. Press the \"Install\" button.",
				 f"3. Search for the add-on file.",
				 f"4. Confirm the selection by pressing the \"Install Add-on\" button in the file browser."]

		for line in lines:
			layout.label(text=line)


class EXAMPLE_OT_install_dependencies(bpy.types.Operator):
	bl_idname = "example.install_dependencies"
	bl_label = "Install dependencies"
	bl_description = "Downloads and ins"
	bl_options = {"REGISTER", "INTERNAL"}

	@classmethod
	def poll(self, context):
		# Deactivate when dependencies have been installed
		return not dependencies_installed

	def execute(self, context):
		try:
			install_pip()
			for dependency in dependencies:
				install_and_import_module(module_name=dependency.module,
										  package_name=dependency.package,
										  global_name=dependency.name)
		except (subprocess.CalledProcessError, ImportError) as err:
			self.report({"ERROR"}, str(err))
			return {"CANCELLED"}

		global dependencies_installed
		dependencies_installed = True

		# Register the panels, operators, etc. since dependencies are installed
		# for cls in dependent_modules:
		# for cls in (EXAMPLE_PT_panel, EXAMPLE_OT_dummy_operator):
		# 	bpy.utils.register_class(cls)

		return {"FINISHED"}


class EXAMPLE_preferences(bpy.types.AddonPreferences):
	bl_idname = __package__

	def draw(self, context):
		layout = self.layout
		layout.operator(EXAMPLE_OT_install_dependencies.bl_idname, icon="CONSOLE")


def register():
	global dependencies_installed
	dependencies_installed = False
	
	for cls in (EXAMPLE_PT_warning_panel, EXAMPLE_OT_install_dependencies, EXAMPLE_preferences):
		bpy.utils.register_class(cls)
	try:
		for dependency in dependencies:
			import_module(module_name=dependency.module, global_name=dependency.name)
		dependencies_installed = True
	except ModuleNotFoundError:
		# Don't register other panels, operators etc.
		return

	# for cls in dependent_modules:
	for cls in dependent_classes:
		if hasattr(cls, 'register'):
			cls.register()
		else:
			bpy.utils.register_class(cls)


def unregister():
	for cls in (EXAMPLE_PT_warning_panel, EXAMPLE_OT_install_dependencies, EXAMPLE_preferences):
		bpy.utils.unregister_class(cls)

	if dependencies_installed:
		# for cls in dependent_modules:
		for cls in dependent_classes:
			if hasattr(cls, 'unregister'):
				cls.unregister()
			else:
				bpy.utils.unregister_class(cls)
		

if __name__ == "__main__":
	register()
