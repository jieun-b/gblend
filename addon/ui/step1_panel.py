import bpy

class GBLEND_PT_ScenePanel(bpy.types.Panel):
    bl_idname = "GBLEND_PT_scene_panel"
    bl_label = "Step 1: Prepare scene"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBlend"

    def draw(self, context):
        layout = self.layout
        paths = context.scene.paths
        settings = context.scene.settings

        box = layout.box()
        box.prop(paths, "output_dir", text="Save To")
        box.label(text="(Used for scene, render, and export results)", icon='INFO')

        box = layout.box()
        box.prop(paths, "data_dir", text="Load Data")
        
        row = layout.row()
        row.prop(settings, "scene_setup_mode", expand=True)

        if settings.scene_setup_mode == 'GENERATE':
            layout.operator("gblend.generate_scene", text="Generate Scene").auto_import = True
        elif settings.scene_setup_mode == 'MANUAL':
            box = layout.box()
            box.prop(paths, "scene_dir", text="Load Scene")
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