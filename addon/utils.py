import os
import bpy


def auto_detect_colmap_root(path: str):
    """
    주어진 경로(path) 기준으로 COLMAP dataset의 루트(images, sparse가 모두 존재하는 폴더)를 탐색.
    - 하위로도 (최대 깊이 5단계) 검색
    - 현재 폴더나 상위 폴더에서도 검사
    """
    if not path or not os.path.exists(path):
        print(f"[WARN] Path not found: {path}")
        return None

    cur_dir = path if os.path.isdir(path) else os.path.dirname(path)

    for _ in range(5):
        images_dir = os.path.join(cur_dir, "images")
        sparse_dir = os.path.join(cur_dir, "sparse")
        if os.path.isdir(images_dir) and os.path.isdir(sparse_dir):
            return cur_dir
        parent = os.path.dirname(cur_dir)
        if parent == cur_dir:
            break
        cur_dir = parent

    for root, dirs, _ in os.walk(path):
        if "images" in dirs and "sparse" in dirs:
            return root
    return None

def on_data_dir_changed(self, context):
    new_root = auto_detect_colmap_root(self.data_dir)
    if new_root:
        if new_root != self.data_dir:
            print(f"[INFO] Auto-detected COLMAP dataset root: {new_root}")
            self.data_dir = new_root
    else:
        print(f"[WARN] No valid COLMAP dataset (images + sparse) found near: {self.data_dir}")


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

def on_gaussian_dir_changed(self, context):
    folder = self.scene_dir
    if not os.path.isdir(folder):
        return
    ply_path, json_path = find_gaussian_outputs(folder)
    if ply_path:
        self.ply_path = ply_path
        settings = context.scene.settings
        settings.scene_name = os.path.splitext(os.path.basename(ply_path))[0]
    if json_path:
        self.camera_path = json_path


def update_selected_camera(self, context):
    camera_name = getattr(self, "start_camera", None) or getattr(self, "end_camera", None)
    cam = bpy.data.objects.get(camera_name)
    if cam:
        bpy.ops.object.select_all(action='DESELECT')
        cam.select_set(True)
        context.view_layer.objects.active = cam

def camera_enum_items(_, context):
    return [
        (obj.name, obj.name, "")
        for obj in bpy.data.objects
        if obj.type == 'CAMERA' and obj.name != "Animated Camera"
    ]