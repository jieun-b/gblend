import bpy

def place_object(glb_path: str, set_active=True):
    """Import GLB file, place it at the scene center (0,0,0), and normalize scale."""
    bpy.ops.import_scene.gltf(filepath=glb_path)
    bpy.context.view_layer.update()

    imported_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    if not imported_objs:
        print("[WARN] No mesh found.")
        return

    obj = max(imported_objs, key=lambda o: o.dimensions.length)
    obj.parent = None
    obj.location = (0.0, 0.0, 0.0)  
    obj.scale = (1.0, 1.0, 1.0)
    bpy.context.view_layer.update()

    size = max(obj.dimensions)
    if size > 0:
        scale = 0.5 / size
        obj.scale = (scale, scale, scale)
    else:
        print("[WARN] Object size zero.")

    for coll in obj.users_collection:
        coll.objects.unlink(obj)
    bpy.context.scene.collection.objects.link(obj)

    if set_active:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

    print(f"[INFO] Object placed at scene center: {obj.name}")
