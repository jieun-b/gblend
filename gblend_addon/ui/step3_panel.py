import bpy

class GBLEND_PT_CameraPanel(bpy.types.Panel):
    bl_idname = "GBLEND_PT_camera_panel"
    bl_label = "Step 3: Animated Camera"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBlend"

    def draw(self, context):
        layout = self.layout
        props = context.scene.gblend_scene_settings

        layout.prop(props, "start_camera", text="Cam1")
        layout.prop(props, "end_camera", text="Cam2")

        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(props, "interpolation_frames", text="Interpolation")

        layout.operator("gblend.animated_camera", text="Generate Animated Camera")