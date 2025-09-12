import bpy

import os
import uuid
import shutil
import zipfile
import requests

from ..utils import on_gaussian_folder_changed

class GBLEND_OT_scene_generate(bpy.types.Operator):
    """Generate Scene from dataset using Gaussian Splatting server"""
    bl_idname = "gblend.generate_scene"
    bl_label = "Generate Scene"
    bl_options = {'REGISTER'}

    auto_import: bpy.props.BoolProperty(
        name="Auto Import",
        description="Automatically import the generated scene into viewport",
        default=True,
    )

    @classmethod
    def poll(cls, context):
        paths = context.scene.gblend_project_paths
        return bool(getattr(paths, "data_dir", "") and os.path.isdir(paths.data_dir))

    def _create_input_zip(self, dataset_path, tmp_dir):
        """Zip dataset into /tmp directory"""
        zip_input_path = os.path.join(tmp_dir, "input.zip")
        shutil.make_archive(zip_input_path.replace(".zip", ""), "zip", dataset_path)
        return zip_input_path

    def _request_gaussian_server(self, zip_input_path, server_url):
        """Send dataset zip to server and get output zip"""
        with open(zip_input_path, "rb") as f:
            files = {"data": f}
            response = requests.post(f"{server_url}/gaussian", files=files)
        if response.status_code != 200:
            raise RuntimeError(f"Server error: {response.status_code}")
        return response.content

    def _extract_output(self, zip_bytes, output_dir):
        """Unzip server response into output_dir"""
        zip_output_path = os.path.join(output_dir, "output.zip")
        with open(zip_output_path, "wb") as f:
            f.write(zip_bytes)
        with zipfile.ZipFile(zip_output_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)

    def execute(self, context):
        scene = context.scene
        paths = scene.gblend_project_paths
        settings = scene.gblend_scene_settings

        dataset_path = paths.data_dir
        job_id = str(uuid.uuid4())[:8]
        tmp_dir = os.path.join("/tmp/gblend", job_id)
        os.makedirs(tmp_dir, exist_ok=True)

        try:
            # Server URL (defined in Scene Settings)
            server_url = getattr(settings, "gaussian_url", "http://localhost:8000")

            # Create dataset zip
            zip_input_path = self._create_input_zip(dataset_path, tmp_dir)

            # Send request to server
            zip_bytes = self._request_gaussian_server(zip_input_path, server_url)

            # Extract output
            output_dir = os.path.join(paths.project_root, "3dgs_output")
            os.makedirs(output_dir, exist_ok=True)
            self._extract_output(zip_bytes, output_dir)

            # Update Blender paths
            paths.gs_output_dir = output_dir
            on_gaussian_folder_changed(paths, context)

            # Refresh viewport
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()

            self.report({'INFO'}, f"Scene generated → {output_dir}")

            # Auto Import
            if self.auto_import:
                bpy.app.timers.register(lambda: (bpy.ops.gblend.scene_align('INVOKE_DEFAULT'), None)[1], first_interval=0.1)

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Scene generation failed: {e}")
            return {'CANCELLED'}