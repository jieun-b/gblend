import bpy
from .dependency import Dependency

class Preferences(bpy.types.AddonPreferences):
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