import bpy
from .dependency import run_pip_command

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