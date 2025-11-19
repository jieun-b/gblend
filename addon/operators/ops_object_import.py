import bpy
import json
import uuid
import requests
from pathlib import Path

from ..core import place_object
from ..config import OBJAVERSE_SERVER_URL
 
class GBLEND_OT_object_import(bpy.types.Operator):
    """Download GLB object from server and place in scene"""
    bl_idname = "gblend.import_object"
    bl_label = "Object Import"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.settings
        paths = context.scene.paths
        return bool(settings.import_object_name.strip()) and bool(paths.output_dir.strip())

    def execute(self, context):
        paths = context.scene.paths
        settings = context.scene.settings

        search_text = settings.import_object_name.strip()
        output_dir = Path(getattr(paths, "output_dir", ""))

        if not output_dir.exists():
            self.report({'ERROR'}, "Invalid project folder.")
            return {'CANCELLED'}

        # Output directory
        objects_dir = output_dir / "objects"
        objects_dir.mkdir(parents=True, exist_ok=True)

        # Request object download
        try:
            response = requests.get(
                f"{OBJAVERSE_SERVER_URL}/download_glb/",
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
