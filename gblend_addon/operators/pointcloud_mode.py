# gblend_addon/operators/pointcloud_mode.py

import bpy
import os

class GBLEND_OT_set_point_cloud_mode(bpy.types.Operator):
    bl_idname = "gblend.set_point_cloud_mode"
    bl_label = "Show As Point Cloud"
    bl_description = "Set the imported PLY object to be displayed as a point cloud using Kiri Engine settings"
    
    def execute(self, context):
        scene = context.scene
        ply_path = scene.gblend_ply_path

        if not ply_path or not os.path.exists(ply_path):
            self.report({'ERROR'}, "PLY path not set or file missing.")
            return {'CANCELLED'}

        obj_name = os.path.splitext(os.path.basename(ply_path))[0]
        obj = bpy.data.objects.get(obj_name)

        if obj is None:
            self.report({'ERROR'}, f"Object '{obj_name}' not found in scene.")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        try:
            obj.sna_kiri3dgs_active_object_update_mode = 'Show As Point Cloud'
            self.report({'INFO'}, f"{obj_name} set to Point Cloud mode.")
        except Exception as e:
            self.report({'ERROR'}, f"Kiri update failed: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}