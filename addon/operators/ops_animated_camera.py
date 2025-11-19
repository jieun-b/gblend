import bpy
import os
from ..core import setup_animated_camera


class GBLEND_OT_animated_camera(bpy.types.Operator):
    """Create an Animated Camera based on two selected reference cameras"""
    bl_idname = "gblend.animate_camera"
    bl_label = "Generate Animated Camera"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        cam_collection = bpy.data.collections.get("Cameras")
        if not cam_collection:
            return False
        cameras = [obj for obj in cam_collection.objects if obj.type == 'CAMERA' and obj.name != "Animated Camera"]
        return len(cameras) > 0

    def execute(self, context):
        cameras = [
            obj for obj in bpy.data.collections.get("Cameras", []).objects
            if obj.type == 'CAMERA' and obj.name != "Animated Camera"
        ]
        if not cameras:
            self.report({'ERROR'}, "No reference cameras found in collection.")
            return {'CANCELLED'}

        parent_collection = bpy.data.collections.get("Collection")
        if parent_collection is None:
            self.report({'ERROR'}, "Default 'Collection' not found in scene")
            return {'CANCELLED'}
        
        setup_animated_camera(cameras, parent_collection)
        self.report({'INFO'}, "Animated Camera generated successfully.")
        return {'FINISHED'}
