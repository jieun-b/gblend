from mathutils import Vector, Matrix
import math
import bpy
import numpy as np
from ..utils import add_obj

def compute_field_of_view(camera):
    sensor_extent = max(camera["width"], camera["height"])
    fov = 2 * math.atan(sensor_extent / (2 * camera["fx"]))  # fx는 focal length
    return fov

def _add_camera_data(camera: dict, camera_name: str):
    bcamera = bpy.data.cameras.new(camera_name)
    bcamera.lens_unit = 'MILLIMETERS'
    bcamera.lens = camera["fx"]
    bcamera.sensor_width = camera["width"] * (camera["fx"] / camera["fy"])

    bcamera.shift_x = (camera["cx"] - camera["width"] / 2.0) / camera["width"]
    bcamera.shift_y = (camera["cy"] - camera["height"] / 2.0) / camera["height"]

    # Store intrinsics in Blender camera custom properties
    bcamera["fx"] = camera["fx"]
    bcamera["fy"] = camera["fy"]
    bcamera["cx"] = camera["cx"]
    bcamera["cy"] = camera["cy"]
    bcamera["width"] = camera["width"]
    bcamera["height"] = camera["height"]

    return bcamera

def add_camera_object(
    camera,
    camera_name,
    camera_collection,
):
    bcamera = _add_camera_data(camera, camera_name)
    camera_object = add_obj(bcamera, camera_name, camera_collection)
 
    camera_object.matrix_world = compute_camera_matrix_world(
        camera["position"], camera["rotation"]
    )
    return camera_object

def copy_camera_object(
    camera,
    camera_name,
    camera_collection,
):
    camera_object = camera.copy()
    camera_object.data = camera.data.copy()
    camera_object.name = camera_name
    camera_collection.objects.link(camera_object)
    return camera_object

def compute_camera_matrix_world(position, rotation, fix_forward=True):
    R = Matrix(rotation).transposed()
    T = Vector(position)

    pose = Matrix((
        R[0].to_4d(),
        R[1].to_4d(),
        R[2].to_4d(),
        Vector((T[0], T[1], T[2], 1.0))
    )).transposed()

    if fix_forward:
        rot_x180 = Matrix.Rotation(math.pi, 4, 'X')  # 180도 회전
        pose = pose @ rot_x180

    return pose

def load_background_image(bg_image, cam_obj):
    camera_data = cam_obj.data
    camera_data.show_background_images = True

    if len(camera_data.background_images) == 0:
        background_image = camera_data.background_images.new()
    else:
        background_image = camera_data.background_images[0]

    background_image.image = bg_image
    background_image.frame_method = "CROP"

def compute_camera_path(start_cam, end_cam, number_interpolation_frames=0, parent_collection=None):
    if not start_cam or not end_cam:
        print("[ERROR] Start or End camera is missing.")
        return []

    path_cameras = [start_cam]

    if parent_collection is None:
        parent_collection = bpy.context.scene.collection

    interp_col = parent_collection.children.get("InterpCams")
    if interp_col is None:
        interp_col = bpy.data.collections.new("InterpCams")
        parent_collection.children.link(interp_col)

    if number_interpolation_frames > 0:
        start_loc = np.array(start_cam.matrix_world.translation)
        end_loc = np.array(end_cam.matrix_world.translation)

        start_rot = start_cam.matrix_world.to_quaternion()
        end_rot = end_cam.matrix_world.to_quaternion()

        for i in range(1, number_interpolation_frames + 1):
            t = i / (number_interpolation_frames + 1)

            interp_loc = (1 - t) * start_loc + t * end_loc
            interp_rot = start_rot.slerp(end_rot, t)

            cam_copy = start_cam.copy()
            cam_copy.data = start_cam.data.copy()
            cam_copy.name = f"Cam_{i:03d}"

            interp_col.objects.link(cam_copy)

            mat = interp_rot.to_matrix().to_4x4()
            mat.translation = interp_loc
            cam_copy.matrix_world = mat

            path_cameras.append(cam_copy)

    path_cameras.append(end_cam)
    return path_cameras

