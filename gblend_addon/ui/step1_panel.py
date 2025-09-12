import bpy

class GBLEND_PT_ProjectPanel(bpy.types.Panel):
    bl_idname = "GBLEND_PT_project_panel"
    bl_label = "Step 1: Project Folder"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBlend"

    def draw(self, context):
        layout = self.layout
        props = context.scene.gblend_project_paths

        box = layout.box()
        box.prop(props, "project_root", text="Root Folder")

        if props.project_root and not props.data_dir:
            box.label(text="COLMAP dataset not detected.")
            box.prop(props, "data_dir", text="Dataset Folder")
