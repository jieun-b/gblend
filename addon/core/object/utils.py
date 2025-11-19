import bpy
from mathutils import Vector

# def place_object(glb_path: str, set_active=True):
#     """Import GLB file, place it at the scene center (0,0,0), and normalize scale."""
#     bpy.ops.import_scene.gltf(filepath=glb_path)
#     bpy.context.view_layer.update()

#     imported_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
#     if not imported_objs:
#         print("[WARN] No mesh found.")
#         return

#     obj = max(imported_objs, key=lambda o: o.dimensions.length)
#     obj.parent = None
#     obj.location = (0.0, 0.0, 0.0)  
#     obj.scale = (1.0, 1.0, 1.0)
#     bpy.context.view_layer.update()

#     size = max(obj.dimensions)
#     if size > 0:
#         scale = 0.5 / size
#         obj.scale = (scale, scale, scale)
#     else:
#         print("[WARN] Object size zero.")

#     for coll in obj.users_collection:
#         coll.objects.unlink(obj)
#     bpy.context.scene.collection.objects.link(obj)

#     if set_active:
#         bpy.context.view_layer.objects.active = obj
#         obj.select_set(True)

#     print(f"[INFO] Object placed at scene center: {obj.name}")



def place_object(glb_path: str, set_active=True):
    """Import GLB file, flatten hierarchy, and normalize scale for all meshes."""
    bpy.ops.import_scene.gltf(filepath=glb_path)
    bpy.context.view_layer.update()

    # 선택된 모든 객체 가져오기
    imported_objs = bpy.context.selected_objects
    if not imported_objs:
        print("[WARN] No imported objects found.")
        return

    # 계층을 flatten (모든 부모 관계 제거)
    for obj in imported_objs:
        obj.parent = None

    # 모든 mesh 객체만 대상으로 크기 계산
    meshes = [obj for obj in imported_objs if obj.type == 'MESH']
    if not meshes:
        print("[WARN] No mesh found after flattening.")
        return

    bpy.context.view_layer.update()

    # 전체 bounding box 기준 크기 계산
    all_coords = []
    for obj in meshes:
        for v in obj.bound_box:
            co_world = obj.matrix_world @ Vector(v)
            all_coords.append(co_world)

    if not all_coords:
        print("[WARN] No bounding box data.")
        return

    xs = [co.x for co in all_coords]
    ys = [co.y for co in all_coords]
    zs = [co.z for co in all_coords]

    size = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    scale = 0.5 / size if size > 0 else 1.0

    # 모든 객체 원점 이동 + 동일 스케일 적용
    for obj in meshes:
        obj.location = (0.0, 0.0, 0.0)
        obj.scale = (scale, scale, scale)
        bpy.context.scene.collection.objects.link(obj)

    if set_active:
        for o in meshes:
            o.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]

    print(f"[INFO] Placed {len(meshes)} meshes at center with unified scale.")