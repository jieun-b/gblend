# gblend_addon/operators/download_object.py

import bpy
import json
import uuid
import requests
from pathlib import Path
from gblend_addon.tasks import place_last_downloaded_obj

class GBLEND_OT_add_object_from_text(bpy.types.Operator):
    bl_idname = "gblend.add_object_from_text"
    bl_label = "Add Object from Text"
    bl_description = "Download GLB from text and place it in the scene"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        text = context.scene.gblend_search_text.strip()
        return bool(text) and bool(context.scene.gblend_project_dir.strip())

    def execute(self, context):
        search_text = context.scene.gblend_search_text.strip()
        project_root = Path(context.scene.gblend_project_dir)

        if not project_root.exists():
            self.report({'ERROR'}, "Invalid project folder.")
            return {'CANCELLED'}

        server_url = "http://localhost:8002/download_glb/"
        try:
            response = requests.get(server_url, params={"query": search_text})
            if response.status_code != 200:
                self.report({'ERROR'}, f"Server error: {response.status_code}")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Connection failed: {e}")
            return {'CANCELLED'}

        objects_dir = project_root / "objects"
        objects_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4().hex[:8]}_{search_text.replace(' ', '_')}.glb"
        save_path = objects_dir / filename

        with open(save_path, "wb") as f:
            f.write(response.content)

        with open(objects_dir / "last_downloaded.json", "w") as f:
            json.dump({
                "text": search_text,
                "path": str(save_path)
            }, f, indent=2)

        self.report({'INFO'}, f"Downloaded and placing: {save_path.name}")

        place_last_downloaded_obj(str(objects_dir), set_active=True)

        return {'FINISHED'}
