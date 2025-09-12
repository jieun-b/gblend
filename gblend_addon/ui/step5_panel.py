import bpy

class GBLEND_PT_RenderPanel(bpy.types.Panel):
    bl_idname = "GBLEND_PT_render_panel"
    bl_label = "Step 5: Render Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBlend"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        render = scene.render
        settings = scene.gblend_scene_settings

        layout.operator("gblend.cull_camera", text="Camera Cull")
        
        row = layout.row(align=True)
        row.operator("gblend.mode_scene", text="Edit Scene",
                     depress=settings.render_mode == 'EDIT').mode = 'EDIT'
        row.operator("gblend.mode_scene", text="Prepare Render",
                     depress=settings.render_mode == 'RENDER').mode = 'RENDER'

        box = layout.box()
        col = box.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.enabled = False
        col.prop(render, "resolution_x", text="Resolution X")
        col.prop(render, "resolution_y", text="Y")

        box = layout.box()
        grid = box.grid_flow(row_major=True, columns=2, even_columns=True, even_rows=True, align=True)
        grid.prop(settings, "save_rgb", text="RGB")
        grid.prop(settings, "save_depth", text="Depth")
        grid.prop(settings, "save_normal", text="Normal")
        grid.prop(settings, "save_segmentation", text="Segmentation")

        layout.operator("gblend.render_scene", text="Render")