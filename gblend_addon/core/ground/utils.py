import numpy as np
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


def translate_object_along_z(obj, z_offset):
    trans_mat = Matrix.Translation(Vector((0, 0, -z_offset)))
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
