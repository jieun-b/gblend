import bpy
import subprocess
import importlib.util
import importlib.metadata
import sys

# ----------------------------------------
# Internal utilities
# ----------------------------------------

def run_pip_command(args):
    try:
        subprocess.check_call([sys.executable, "-m", "ensurepip"])
        subprocess.check_call([sys.executable, "-m", "pip"] + args)
        return True, ""
    except Exception as e:
        return False, str(e)


# ----------------------------------------
# Dependency descriptor
# ----------------------------------------

class Dependency:
    def __init__(self, package_name, gui_name=None, import_name=None):
        self.package_name = package_name
        self.import_name = import_name or package_name
        self.gui_name = gui_name or package_name.title()

    def is_installed(self):
        return importlib.util.find_spec(self.import_name) is not None

    def get_version_and_location(self):
        try:
            dist = importlib.metadata.distribution(self.package_name)
            return dist.version, str(dist.locate_file(''))
        except Exception:
            return "N/A", ""



# ----------------------------------------
# Operators
# ----------------------------------------

class InstallDependencyOperator(bpy.types.Operator):
    bl_idname = "gblend.install_dependency"
    bl_label = "Install Dependency"

    dependency_package_name: bpy.props.StringProperty()

    def execute(self, context):
        success, msg = run_pip_command(["install", self.dependency_package_name])
        if success:
            self.report({'INFO'}, f"Installed {self.dependency_package_name}")
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == 'PREFERENCES':
                        area.tag_redraw()
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, msg)
            return {'CANCELLED'}



class UninstallDependencyOperator(bpy.types.Operator):
    bl_idname = "gblend.uninstall_dependency"
    bl_label = "Remove Dependency"

    dependency_package_name: bpy.props.StringProperty()

    def execute(self, context):
        success, msg = run_pip_command(["uninstall", "-y", self.dependency_package_name])
        if success:
            self.report({'INFO'}, f"Uninstalled {self.dependency_package_name}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, msg)
            return {'CANCELLED'}


# ----------------------------------------
# Preferences Panel
# ----------------------------------------

class GBlendAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "gblend_addon"

    def get_dependencies(self):
        return [
            Dependency("requests"),
            Dependency("pycocotools"),
        ]

    def draw(self, context):
        layout = self.layout
        layout.label(text="Dependencies:")

        for dep in self.get_dependencies():
            version, location = dep.get_version_and_location()
            is_installed = dep.is_installed()

            box = layout.box()
            row = box.row()
            row.label(text=dep.gui_name)
            row.label(text="Installed" if is_installed else "Not installed")
            row.label(text=version)
            row.label(text=location)

            row = box.row()
            op_install = row.operator("gblend.install_dependency", text=f"Install {dep.gui_name}")
            op_install.dependency_package_name = dep.package_name

            op_remove = row.operator("gblend.uninstall_dependency", text=f"Remove {dep.gui_name}")
            op_remove.dependency_package_name = dep.package_name
