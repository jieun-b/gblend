import bpy
import json
import uuid
import requests
from pathlib import Path

from gblend_addon.core import place_object


class GBLEND_OT_object_import(bpy.types.Operator):
    """Download GLB object from server and place in scene"""
    bl_idname = "gblend.import_object"
    bl_label = "Object Import"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.gblend_scene_settings
        paths = context.scene.gblend_project_paths
        return bool(settings.import_object_name.strip()) and bool(paths.project_root.strip())

    def execute(self, context):
        paths = context.scene.gblend_project_paths
        settings = context.scene.gblend_scene_settings

        search_text = settings.import_object_name.strip()
        project_root = Path(getattr(paths, "project_root", ""))

        if not project_root.exists():
            self.report({'ERROR'}, "Invalid project folder.")
            return {'CANCELLED'}

        # Output directory
        objects_dir = project_root / "objects"
        objects_dir.mkdir(parents=True, exist_ok=True)

        # Object Import endpoint
        import_url = getattr(settings, "object_import_url", "http://localhost:8002")

        # Request object download
        try:
            response = requests.get(
                f"{import_url}/download_glb/",
                params={"query": search_text},
            )
            if response.status_code != 200:
                self.report({'ERROR'}, f"Server error: {response.status_code}")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Request failed: {e}")
            return {'CANCELLED'}

        # Save GLB file
        filename = f"{uuid.uuid4().hex[:8]}_{search_text.replace(' ', '_')}.glb"
        save_path = objects_dir / filename
        with open(save_path, "wb") as f:
            f.write(response.content)

        # Save metadata
        with open(objects_dir / "last_downloaded.json", "w") as f:
            json.dump({"text": search_text, "path": str(save_path)}, f, indent=2)

        # Place object
        try:
            place_object(str(save_path), set_active=True)
            self.report({'INFO'}, f"Downloaded and placed: {save_path.name}")
        except Exception as e:
            self.report({'ERROR'}, f"Placing object failed: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}
