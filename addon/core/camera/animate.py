import bpy
import os
from collections import namedtuple
from mathutils import Matrix, Quaternion

from .utils import copy_camera_object, compute_field_of_view, load_background_image

_CameraIntrinsics = namedtuple("CameraIntrinsics", "field_of_view shift_x shift_y")

def _remove_quaternion_discontinuities(target_obj):
    # the interpolation of quaternions may lead to discontinuities
    # if the quaternions show different signs

    # https://blender.stackexchange.com/questions/58866/keyframe-interpolation-instability
    action = target_obj.animation_data.action

    # quaternion curves
    fqw = action.fcurves.find("rotation_quaternion", index=0)
    fqx = action.fcurves.find("rotation_quaternion", index=1)
    fqy = action.fcurves.find("rotation_quaternion", index=2)
    fqz = action.fcurves.find("rotation_quaternion", index=3)

    # invert quaternion so that interpolation takes the shortest path
    if len(fqw.keyframe_points) > 0:
        current_quat = Quaternion(
            (
                fqw.keyframe_points[0].co[1],
                fqx.keyframe_points[0].co[1],
                fqy.keyframe_points[0].co[1],
                fqz.keyframe_points[0].co[1],
            )
        )

        for i in range(len(fqw.keyframe_points) - 1):
            last_quat = current_quat
            current_quat = Quaternion(
                (
                    fqw.keyframe_points[i + 1].co[1],
                    fqx.keyframe_points[i + 1].co[1],
                    fqy.keyframe_points[i + 1].co[1],
                    fqz.keyframe_points[i + 1].co[1],
                )
            )

            if last_quat.dot(current_quat) < 0:
                current_quat.negate()
                fqw.keyframe_points[i + 1].co[1] = -fqw.keyframe_points[
                    i + 1
                ].co[1]
                fqx.keyframe_points[i + 1].co[1] = -fqx.keyframe_points[
                    i + 1
                ].co[1]
                fqy.keyframe_points[i + 1].co[1] = -fqy.keyframe_points[
                    i + 1
                ].co[1]
                fqz.keyframe_points[i + 1].co[1] = -fqz.keyframe_points[
                    i + 1
                ].co[1]

def _set_fcurve_interpolation(some_obj, interpolation_type="LINEAR"):
    # interpolation_string: ['CONSTANT', 'LINEAR', 'BEZIER', 'SINE',
    # 'QUAD', 'CUBIC', 'QUART', 'QUINT', 'EXPO', 'CIRC',
    # 'BACK', 'BOUNCE', 'ELASTIC']
    fcurves = some_obj.animation_data.action.fcurves
    for fcurve in fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = interpolation_type


def _add_transformation_animation(
    animated_obj_name,
    transformations_sorted,
    interpolation_type=None,
    remove_rotation_discontinuities=True,
):
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = len(transformations_sorted)
    animated_obj = bpy.data.objects[animated_obj_name]

    for frame_idx, transformation in enumerate(transformations_sorted, start=1):
        if transformation is None:
            continue

        loc, rot, _ = Matrix(transformation).decompose()
        animated_obj.location = loc
        animated_obj.rotation_mode = "QUATERNION"
        animated_obj.rotation_quaternion = rot

        animated_obj.keyframe_insert(data_path="location", index=-1, frame=frame_idx)
        animated_obj.keyframe_insert(data_path="rotation_quaternion", index=-1, frame=frame_idx)

        if remove_rotation_discontinuities:
            _remove_quaternion_discontinuities(animated_obj)

        if interpolation_type is not None:
            _set_fcurve_interpolation(animated_obj, interpolation_type)


def _add_camera_intrinsics_animation(
    animated_obj_name, intrinsics_sorted
):
    animated_obj = bpy.data.objects[animated_obj_name]

    for frame_idx, intrinsics in enumerate(intrinsics_sorted, start=1):
        if intrinsics is None:
            continue

        animated_obj.data.angle = intrinsics.field_of_view
        animated_obj.data.shift_x = intrinsics.shift_x
        animated_obj.data.shift_y = intrinsics.shift_y

        animated_obj.data.keyframe_insert(
            data_path="lens", index=-1, frame=frame_idx
        )
        animated_obj.data.keyframe_insert(
            data_path="shift_x", index=-1, frame=frame_idx
        )
        animated_obj.data.keyframe_insert(
            data_path="shift_y", index=-1, frame=frame_idx
        )


def add_camera_animation(
    cameras,
    parent_collection=None,
    interpolation_type="LINEAR",
    remove_rotation_discontinuities=True,
):
    cameras_sorted = list(cameras)

    animated_camera = bpy.data.objects.get("Animated Camera")
    if animated_camera:
        animated_camera.animation_data_clear()
    else:
        start_cam = cameras_sorted[0]  
        if parent_collection is None:
            parent_collection = bpy.data.collections.get("Collection")
        cam_obj = copy_camera_object(
            start_cam, "Animated Camera", parent_collection
        )

        if hasattr(start_cam.data, "background_images") and start_cam.data.background_images:
            bg = start_cam.data.background_images[0]
            if bg.image:
                bg_image = bpy.data.images.load(bg.image.filepath)
                load_background_image(bg_image, cam_obj)

        animated_camera = cam_obj

    transformations_sorted = []
    camera_intrinsics_sorted = []

    for cam in cameras_sorted:
        matrix_world = cam.matrix_world.copy()
        fov = compute_field_of_view(cam.data)

        width = getattr(cam.data, "width", None)
        height = getattr(cam.data, "height", None)
        cx = getattr(cam.data, "cx", width / 2 if width else 0)
        cy = getattr(cam.data, "cy", height / 2 if height else 0)

        shift_x = (cx - (width / 2.0)) / width if width else 0
        shift_y = (cy - (height / 2.0)) / height if height else 0

        camera_intrinsics = _CameraIntrinsics(fov, shift_x, shift_y)
        transformations_sorted.append(matrix_world)
        camera_intrinsics_sorted.append(camera_intrinsics)

    _add_transformation_animation(
        animated_obj_name=animated_camera.name,
        transformations_sorted=transformations_sorted,
        interpolation_type=interpolation_type,
        remove_rotation_discontinuities=remove_rotation_discontinuities,
    )

    _add_camera_intrinsics_animation(
        animated_obj_name=animated_camera.name,
        intrinsics_sorted=camera_intrinsics_sorted,
    )

    return animated_camera