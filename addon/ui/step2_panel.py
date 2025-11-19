import bpy

class GBLEND_PT_CameraPanel(bpy.types.Panel):
    bl_idname = "GBLEND_PT_camera_panel"
    bl_label = "Step 2: Create Animated Camera"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBlend"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.settings

        layout.prop(settings, "start_camera", text="Cam1")
        layout.prop(settings, "end_camera", text="Cam2")

        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(settings, "interpolation_frames", text="Interpolation")

        layout.operator("gblend.animate_camera", text="Create Animated Camera")