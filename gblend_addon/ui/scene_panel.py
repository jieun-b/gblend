import bpy

class GBLEND_PT_ScenePanel(bpy.types.Panel):
    bl_idname = "GBLEND_PT_scene_panel"
    bl_label = "Step 2: Generate Scene from Data"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBlend"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.gblend_scene_settings
        paths = context.scene.gblend_project_paths

        layout.prop(props, "scene_setup_mode", expand=True)

        if props.scene_setup_mode == 'GENERATE':
            layout.operator("gblend.generate_scene", text="Generate Scene")
        elif props.scene_setup_mode == 'MANUAL':
            box = layout.box()
            box.prop(paths, "gs_output_dir", text="3DGS Output Folder")