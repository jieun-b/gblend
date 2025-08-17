import bpy

class GBLEND_PT_ProjectPanel(bpy.types.Panel):
    bl_idname = "GBLEND_PT_project_panel"
    bl_label = "Step 1: Select Project Folder"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBlend"

    def draw(self, context):
        layout = self.layout
        props = context.scene.gblend_project_paths

        box = layout.box()
        box.prop(props, "project_root", text="Project Root")

        if props.project_root and not props.data_dir:
            box.label(text="Could not detect COLMAP dataset automatically.")
            box.prop(props, "data_dir", text="Select Dataset Folder")