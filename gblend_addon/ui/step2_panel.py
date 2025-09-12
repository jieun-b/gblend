import bpy

class GBLEND_PT_ScenePanel(bpy.types.Panel):
    bl_idname = "GBLEND_PT_scene_panel"
    bl_label = "Step 2: Scene Preparation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBlend"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.gblend_scene_settings
        paths = context.scene.gblend_project_paths

        row = layout.row()
        row.prop(props, "scene_setup_mode", expand=True)

        if props.scene_setup_mode == 'GENERATE':
            layout.operator("gblend.generate_scene", text="Generate Scene").auto_import = True
        elif props.scene_setup_mode == 'MANUAL':
            box = layout.box()
            box.prop(paths, "gs_output_dir", text="3DGS Output Folder")
            box.operator("gblend.import_scene", text="Load Scene to 3D Viewport")

        layout.separator() 
        
        row = layout.row(align=True)
        op = row.operator(
            "gblend.display_scene",
            text="Show As Point Cloud",
            depress=bool(
                context.object and getattr(
                    context.object,
                    "sna_kiri3dgs_active_object_update_mode",
                    ""
                ) == "Show As Point Cloud"
            ),
        )
        op.mode = 'Show As Point Cloud'

        op = row.operator(
            "gblend.display_scene",
            text="Enable Camera Updates",
            depress=bool(
                context.object and getattr(
                    context.object,
                    "sna_kiri3dgs_active_object_update_mode",
                    ""
                ) == "Enable Camera Updates"
            ),
        )
        op.mode = 'Enable Camera Updates'

        layout.operator("gblend.align_scene", text="Align Scene to XY Axes")