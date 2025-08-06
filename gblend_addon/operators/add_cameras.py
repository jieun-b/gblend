# gblend_addon/operators/add_cameras.py

import bpy
import os
from gblend_addon.tasks import setup_cameras

class GBLEND_OT_add_cameras(bpy.types.Operator):
    bl_idname = "gblend.add_cameras"
    bl_label = "Add Cameras from JSON"
    bl_description = "Load reconstructed cameras and optionally create an animated camera"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        json_path = scene.gblend_camera_path
        image_dir = os.path.join(scene.gblend_data_path, "images")

        if not os.path.exists(json_path):
            self.report({'ERROR'}, f"Camera JSON not found: {json_path}")
            return {'CANCELLED'}

        if not os.path.isdir(image_dir):
            self.report({'ERROR'}, f"Image folder not found: {image_dir}")
            return {'CANCELLED'}

        parent_collection = bpy.data.collections.get("Collection")
        if parent_collection is None:
            self.report({'ERROR'}, "Default 'Collection' not found in scene")
            return {'CANCELLED'}

        setup_cameras(
            json_path,
            image_dir,
            parent_collection,
            add_camera_motion_as_animation=True
        )

        self.report({'INFO'}, "Cameras loaded successfully.")
        return {'FINISHED'}
