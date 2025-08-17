import bpy

class GBLEND_PT_RenderPanel(bpy.types.Panel):
    bl_idname = "GBLEND_PT_render_panel"
    bl_label = "Step 6: Render Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBlend"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        render = scene.render

        row = layout.row(align=True)
        row.operator(
            "gblend.set_scene_mode",
            text="Edit Scene",
            depress=context.scene.gblend_scene_settings.render_mode == 'EDIT'
        ).mode = 'EDIT'
        row.operator(
            "gblend.set_scene_mode",
            text="Prepare Render",
            depress=context.scene.gblend_scene_settings.render_mode == 'RENDER'
        ).mode = 'RENDER'

        box = layout.box()
        col = box.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.enabled = False

        col.prop(render, "resolution_x", text="Resolution X")
        col.prop(render, "resolution_y", text="Y")

        box.operator("gblend.render_scene", text="Render")