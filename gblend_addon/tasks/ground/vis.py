import bpy
import bmesh
import numpy as np
from PIL import Image, ImageDraw
from mathutils import Vector
from ..shared import add_collection

def draw_sampled_points(mask_path, mask_shape, sampled_pixels):
    vis_img = Image.new("RGB", (mask_shape[1], mask_shape[0]), color=(0, 0, 0))
    draw = ImageDraw.Draw(vis_img)
    for x, y in sampled_pixels:
        r = 2  # 반지름
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 0, 0))

    save_path = mask_path.replace("_mask.png", "_sampled_points.png")
    vis_img.save(save_path)
    print(f"[INFO] Saved sampled points image: {save_path}")


def draw_rays_from_pixels(cam_name, ray_origin, ray_dir, i, length=10.0, color=(1, 0, 0)):
    collection = add_collection(f"Rays_Cam_{cam_name}", parent_collection=bpy.context.scene.collection)

    start = Vector(ray_origin)
    end = Vector(ray_origin + ray_dir * length)

    curve_data = bpy.data.curves.new(f"ray_curve_{i}", type='CURVE')
    curve_data.dimensions = '3D'
    polyline = curve_data.splines.new('POLY')
    polyline.points.add(1)
    polyline.points[0].co = (*start, 1)
    polyline.points[1].co = (*end, 1)

    obj = bpy.data.objects.new(f"Ray_{i}", curve_data)
    collection.objects.link(obj)

    mat = bpy.data.materials.new(name=f"RayMat_{i}")
    mat.diffuse_color = (*color, 1.0)
    obj.data.materials.append(mat)
    obj.color = (*color, 1.0)


def draw_camera_pixel_points(cam, pixels, distance=1.0, name="PixelPoints"):
    mesh = bpy.data.meshes.new(f"{name}_{cam.name}")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    fx = cam.data["fx"]
    fy = cam.data["fy"]
    cx = cam.data["cx"]
    cy = cam.data["cy"]

    bm = bmesh.new()

    for u, v in pixels:
        x = (u - cx) / fx
        y = (cy - v) / fy
        ray = Vector((x, y, -1)).normalized()
        point_local = ray * distance
        point_world = cam.matrix_world @ point_local
        bm.verts.new(point_world)

    bm.to_mesh(mesh)
    bm.free()

    obj.display_type = 'WIRE'
    obj.show_in_front = True
    obj.hide_select = True
    obj.name = name

    return obj


def visualize_points(points, name="GroundPoints", limit=500):
    if limit is not None and len(points) > limit:
        indices = np.random.choice(len(points), size=limit, replace=False)
        points = points[indices]

    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    if name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[name], do_unlink=True)

    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    for pt in points:
        bm.verts.new(Vector(pt))
    bm.verts.ensure_lookup_table()

    bm.to_mesh(mesh)
    bm.free()

    obj.display_type = 'WIRE'
    obj.show_instancer_for_render = False
    obj.show_instancer_for_viewport = False

    print(f"[INFO] Visualized {len(points)} points in '{name}' as vertices.")
