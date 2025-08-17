import bpy

class GBLEND_PT_CameraPanel(bpy.types.Panel):
    bl_idname = "GBLEND_PT_camera_panel"
    bl_label = "Step 4: Add Animated Camera"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBlend"

    def draw(self, context):
        layout = self.layout
        props = context.scene.gblend_scene_settings

        box = layout.box()

        row = box.row(align=True)
        row.use_property_split = True
        row.use_property_decorate = False
        row.prop(props, "frame_start", text="Frame Range") 
        row.prop(props, "frame_end", text="")

        col = box.column()
        col.use_property_split = True
        col.use_property_decorate = False

        col.prop(props, "stride", text="Stride")
        col.prop(props, "interpolation_frames", text="Interpolation")

        box.operator("gblend.add_animated_camera", text="Import Animated Camera")