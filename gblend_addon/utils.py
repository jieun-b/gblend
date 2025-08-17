import os

def find_colmap_dataset(data_root):
    if not os.path.isdir(data_root):
        return None
    if os.path.isdir(os.path.join(data_root, "images")) and os.path.isdir(os.path.join(data_root, "sparse")):
        return data_root
    return None

def find_gaussian_outputs(root):
    ply_candidates = []
    camera_json = None
    for current_root, _, files in os.walk(root):
        for name in files:
            full_path = os.path.join(current_root, name)
            if name.lower().endswith(".ply"):
                ply_candidates.append(full_path)
            if name == "cameras.json" and not camera_json:
                camera_json = full_path
    ply_path = None
    if ply_candidates:
        ply_candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        ply_path = ply_candidates[0]
    return ply_path, camera_json

def on_project_folder_changed(self, context):
    root = self.project_root
    if not os.path.isdir(root):
        return
    colmap_path = find_colmap_dataset(os.path.join(root, "colmap_data"))
    if colmap_path:
        self.data_dir = colmap_path
    else:
        print(f"[WARN] No valid COLMAP dataset found in {root}/colmap_data")
    gs_output = os.path.join(root, "3dgs_output")
    if os.path.isdir(gs_output):
        self.gs_output_dir = gs_output

    output_dir = os.path.join(root, "output")
    self.output_dir = output_dir

def on_gaussian_folder_changed(self, context):
    folder = self.gs_output_dir
    if not os.path.isdir(folder):
        return
    ply_path, json_path = find_gaussian_outputs(folder)
    if ply_path:
        self.ply_path = ply_path
        # Set scene_name in gblend_scene_settings to the PLY file's base name
        scene_settings = context.scene.gblend_scene_settings
        scene_settings.scene_name = os.path.splitext(os.path.basename(ply_path))[0]
    if json_path:
        self.camera_path = json_path