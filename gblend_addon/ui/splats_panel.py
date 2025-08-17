import bpy

class GBLEND_PT_SplatsPanel(bpy.types.Panel):
    bl_idname = "GBLEND_PT_splats_panel"
    bl_label = "Step 3: Import Scene (Splats & Reference Cameras)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBlend"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("gblend.kiri_import_direct", text="Load Scene to 3D Viewport")

        row = layout.row(align=True)
        op = row.operator(
            "gblend.set_kiri_mode",
            text="Show As Point Cloud",
            depress=bool(context.object and getattr(context.object, "sna_kiri3dgs_active_object_update_mode", "") == "Show As Point Cloud")
        )
        op.mode = 'Show As Point Cloud'

        op = row.operator(
            "gblend.set_kiri_mode",
            text="Enable Camera Updates",
            depress=bool(context.object and getattr(context.object, "sna_kiri3dgs_active_object_update_mode", "") == "Enable Camera Updates")
        )
        op.mode = 'Enable Camera Updates'