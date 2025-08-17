import bpy

class GBLEND_PT_SceneAdjustPanel(bpy.types.Panel):
    bl_idname = "GBLEND_PT_scene_adjust_panel"
    bl_label = "Step 5: Scene Adjustment"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBlend"

    def draw(self, context):
        layout = self.layout
        layout.operator("gblend.align_scene_to_ground", text="Align Scene to XY Axes")
        layout.operator("gblend.camera_cull_light", text="Camera Cull")