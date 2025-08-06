from mathutils import Vector, Matrix
import math
import bpy
from ..shared import add_obj

def compute_field_of_view(camera):
    sensor_extent = max(camera["width"], camera["height"])
    fov = 2 * math.atan(sensor_extent / (2 * camera["fx"]))  # fx는 focal length
    return fov

def _add_camera_data(camera: dict, camera_name: str):
    """Add a camera as Blender data entity from a dict."""
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
    """Add a camera as Blender object."""
    bcamera = _add_camera_data(camera, camera_name)
    camera_object = add_obj(bcamera, camera_name, camera_collection)
 
    camera_object.matrix_world = compute_camera_matrix_world(
        camera["position"], camera["rotation"]
    )
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
    """Attach a background image to a Blender camera object."""
    camera_data = cam_obj.data
    camera_data.show_background_images = True

    if len(camera_data.background_images) == 0:
        background_image = camera_data.background_images.new()
    else:
        background_image = camera_data.background_images[0]

    background_image.image = bg_image
    background_image.frame_method = "CROP"
