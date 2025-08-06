# gblend_addon/ui.py

import bpy

class GBLEND_PT_panel(bpy.types.Panel):
    bl_idname = "GBLEND_PT_panel"
    bl_label = "GBlend Addon"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GBlend"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # --- Step 1: Select Project Folder ---
        box = layout.box()
        box.label(text="Step 1: Select Project Folder")
        box.prop(scene, "gblend_project_dir", text="Project Root")

        # Optional - Show data path if not auto-detected
        if scene.gblend_project_dir and not scene.gblend_data_path:
            subbox = box.box()
            subbox.label(text="Could not detect COLMAP dataset automatically.")
            subbox.prop(scene, "gblend_data_path", text="Select Dataset Folder")

        # --- Step 2: Generate Scene from Data ---
        box = layout.box()
        box.label(text="Step 2: Generate Scene from Data")
        box.prop(scene, "gblend_scene_setup_mode", expand=True)

        if scene.gblend_scene_setup_mode == 'GENERATE':
            subbox = box.box()
            subbox.operator("gblend.generate_scene", text="Generate Scene")
        elif scene.gblend_scene_setup_mode == 'MANUAL':
            subbox = box.box()
            subbox.prop(scene, "gblend_gaussian_output_dir", text="3DGS Output Folder")

        # --- Step 3: Manually Import PLY As Splats ---
        box = layout.box()
        box.label(text="Step 3: Import Splats with Kiri Engine")

        subbox = box.box()
        col = subbox.column()
        col.label(text="In Kiri Engine:")
        col.label(text=" 1. Click 'Import PLY As Splats'")
        col.label(text=" 2. Select the file shown below:")

        if scene.gblend_ply_path:
            col.label(text="    " + scene.gblend_ply_path)
        else:
            col.label(text="    Please generate or select a 3DGS output folder.")
        box.operator("gblend.set_point_cloud_mode", text="Show As Point Cloud")

        # --- Step 4: Add Cameras to Scene ---
        box = layout.box()
        box.label(text="Step 4: Add Cameras to Scene")
        box.operator("gblend.add_cameras", text="Import Cameras to Scene")

        # --- Step 5: Align Scene with Ground ---
        box = layout.box()
        box.label(text="Step 5: Align Scene with Ground")
        box.operator("gblend.align_scene_to_ground", text="Align Scene to Ground")

        # --- Step 6: Search & Download 3D Object ---
        box = layout.box()
        box.label(text="Step 6: Search & Download 3D Object")

        row = box.row()
        row.prop(scene, "gblend_search_text", text="Search")
        row.operator("gblend.download_glb_from_text", text="Download")
