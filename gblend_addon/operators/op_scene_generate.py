import bpy

import os
import uuid
import shutil
import zipfile
import requests

from ..utils import on_gaussian_folder_changed

class GBLEND_OT_scene_generate(bpy.types.Operator):
    bl_idname = "gblend.generate_scene"
    bl_label = "Generate Scene from 3D Gaussian Splatting"
    bl_description = "Run Gaussian Splatting externally and save paths to PLY and camera.json"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        paths = context.scene.gblend_project_paths
        p = getattr(paths, "data_dir", "")
        return bool(p and os.path.isdir(p))
    
    def execute(self, context):
        scene = context.scene
        paths = scene.gblend_project_paths

        dataset_path = paths.data_dir

        try:
            job_id = str(uuid.uuid4())[:8]
            tmp_dir = os.path.join("/tmp/gblend", job_id)
            os.makedirs(tmp_dir, exist_ok=True)

            zip_input_path = os.path.join(tmp_dir, "input.zip")
            shutil.make_archive(zip_input_path.replace(".zip", ""), 'zip', dataset_path)

            with open(zip_input_path, 'rb') as f:
                files = {"data": f}
                response = requests.post("http://localhost:8000/gaussian", files=files)

            if response.status_code != 200:
                self.report({'ERROR'}, f"Server error: {response.status_code}")
                return {'CANCELLED'}

            zip_output_path = os.path.join(tmp_dir, "output.zip")
            with open(zip_output_path, "wb") as f:
                f.write(response.content)

            output_dir = os.path.join(paths.project_root, "3dgs_output")
            os.makedirs(output_dir, exist_ok=True)

            with zipfile.ZipFile(zip_output_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)

            paths.gs_output_dir = output_dir
            on_gaussian_folder_changed(paths, context)

            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()

            self.report({'INFO'}, "Scene generated and paths saved.")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Unexpected error: {str(e)}")
            return {'CANCELLED'}