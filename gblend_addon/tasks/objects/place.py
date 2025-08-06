import bpy
import os
import json
from mathutils import Vector

def place_last_downloaded_obj(data_dir: str, set_active=True):
    json_path = os.path.join(data_dir, "last_downloaded.json")
    if not os.path.exists(json_path):
        print("[WARN] No download info found.")
        return

    with open(json_path, "r") as f:
        glb_path = json.load(f)["path"]

    bpy.ops.import_scene.gltf(filepath=glb_path)
    bpy.context.view_layer.update()

    imported_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    if not imported_objs:
        print("[WARN] No mesh found.")
        return

    obj = max(imported_objs, key=lambda o: o.dimensions.length)
    obj.parent = None
    obj.location = (2.0, -2.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    bpy.context.view_layer.update()

    size = max(obj.dimensions)
    if size > 0:
        scale = 0.5 / size
        obj.scale = (scale,) * 3
    else:
        print("[WARN] Object size zero.")

    for coll in obj.users_collection:
        coll.objects.unlink(obj)
    bpy.context.scene.collection.objects.link(obj)

    if set_active:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

    print(f"[INFO] Object placed: {obj.name}")
