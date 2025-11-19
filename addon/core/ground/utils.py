import numpy as np
import bpy
from mathutils import Vector, Matrix

def apply_rotation_to_points(points, rot_mat):
    if isinstance(rot_mat, Matrix):
        rot_mat = np.array(rot_mat.to_3x3())
    elif rot_mat.shape == (4, 4):
        rot_mat = rot_mat[:3, :3]
    return np.dot(points, rot_mat.T)


def compute_rotation_matrix_between(from_vec, to_vec=np.array([0, 0, 1])):
    a = Vector(from_vec).normalized()
    b = Vector(to_vec).normalized()
    q = a.rotation_difference(b)
    return q.to_matrix().to_4x4()


def apply_rotation_to_object(obj, rot_mat):
    obj.matrix_world = rot_mat @ obj.matrix_world


def translate_object_along_z(obj, z_offset, extra_offset=0.1):
    trans_mat = Matrix.Translation(Vector((0, 0, -(z_offset + extra_offset))))
    obj.matrix_world = trans_mat @ obj.matrix_world


def get_camera_ray_from_pixel(cam, pixel):
    """
    cam: Blender 카메라 오브젝트 (bpy.types.Object)
    pixel: (x, y) 좌표 (이미지 기준)
    """
    fx = cam.data["fx"]
    fy = cam.data["fy"]
    cx = cam.data["cx"]
    cy = cam.data["cy"]

    x = (pixel[0] - cx) / fx
    y = (cy - pixel[1]) / fy

    ray_camera = Vector((x, y, -1.0)).normalized()
    ray_origin = cam.matrix_world.translation
    ray_direction = (cam.matrix_world.to_3x3() @ ray_camera).normalized()

    return np.array(ray_origin), np.array(ray_direction)


def add_shadow_catcher_ground(size=10.0, z=0.0, name="Plane"):
    # Find or create the plane
    plane = bpy.data.objects.get(name)
    if plane is None:
        bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
        plane = bpy.context.active_object
        plane.name = name

    # Always create a new ShadowCatcher material
    mat = bpy.data.materials.new("ShadowCatcher")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Nodes
    output = nodes.new(type="ShaderNodeOutputMaterial")
    mix_shader = nodes.new(type="ShaderNodeMixShader")
    transparent = nodes.new(type="ShaderNodeBsdfTransparent")
    diffuse = nodes.new(type="ShaderNodeBsdfDiffuse")
    light_path = nodes.new(type="ShaderNodeLightPath")

    # Layout
    output.location = (400, 0)
    mix_shader.location = (200, 0)
    transparent.location = (0, 100)
    diffuse.location = (0, -100)
    light_path.location = (-200, 0)

    # Links
    links.new(transparent.outputs[0], mix_shader.inputs[1])
    links.new(diffuse.outputs[0], mix_shader.inputs[2])
    links.new(mix_shader.outputs[0], output.inputs[0])
    links.new(light_path.outputs["Is Shadow Ray"], mix_shader.inputs[0])

    # Diffuse → 그림자 색 (어두운 회색)
    diffuse.inputs["Color"].default_value = (0, 0, 0, 1)

    # Assign to plane
    if plane.data.materials:
        plane.data.materials[0] = mat
    else:
        plane.data.materials.append(mat)

    print(f"[INFO] Shadow catcher material assigned to {plane.name}")
    return plane
