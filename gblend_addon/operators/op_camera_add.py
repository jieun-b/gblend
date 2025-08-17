import bpy
import os
from gblend_addon.core import setup_animated_camera

class GBLEND_OT_animated_camera_add(bpy.types.Operator):
    bl_idname = "gblend.add_animated_camera"
    bl_label = "Add Animated Camera from JSON"
    bl_description = "Create an animated camera"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        paths = context.scene.gblend_project_paths
        p = getattr(paths, "camera_path", "")
        return bool(p and os.path.exists(p))

    def execute(self, context):
        scene = context.scene
        paths = scene.gblend_project_paths

        cameras = [
            obj for obj in bpy.data.collections.get("Cameras", []).objects
            if obj.type == 'CAMERA' and obj.name != "Animated Camera"
        ]
        setup_animated_camera(cameras)

        self.report({'INFO'}, "Animated Camera loaded successfully.")
        return {'FINISHED'}