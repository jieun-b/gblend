import bpy
from collections import namedtuple
from mathutils import Matrix, Quaternion

from .utils import add_camera_object, compute_camera_matrix_world, compute_field_of_view

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
    number_interpolation_frames,
    interpolation_type=None,
    remove_rotation_discontinuities=True,
):
    scene = bpy.context.scene
    scene.frame_start = 0
    step_size = number_interpolation_frames + 1
    scene.frame_end = step_size * len(transformations_sorted)
    animated_obj = bpy.data.objects[animated_obj_name]

    for index, transformation in enumerate(transformations_sorted):
        # log_report('INFO', 'index: ' + str(index), op)
        # log_report('INFO', 'transformation: ' + str(transformation), op)

        current_keyframe_index = (index + 1) * step_size

        if transformation is None:
            continue

        # A direct assignment of a numpy array leads to incorrect results!
        animated_obj.matrix_world = Matrix(transformation)

        animated_obj.keyframe_insert(
            data_path="location", index=-1, frame=current_keyframe_index
        )

        # Don't use euler rotations, they show too many discontinuties
        # animated_obj.keyframe_insert(
        #   data_path="rotation_euler",
        #   index=-1,
        #   frame=current_keyframe_index)

        animated_obj.rotation_mode = "QUATERNION"
        animated_obj.keyframe_insert(
            data_path="rotation_quaternion",
            index=-1,
            frame=current_keyframe_index,
        )

        if remove_rotation_discontinuities:
            # q and -q represent the same rotation
            _remove_quaternion_discontinuities(animated_obj)

        if interpolation_type is not None:
            _set_fcurve_interpolation(animated_obj, interpolation_type)


def _add_camera_intrinsics_animation(
    animated_obj_name, intrinsics_sorted, number_interpolation_frames,
):
    step_size = number_interpolation_frames + 1
    animated_obj = bpy.data.objects[animated_obj_name]

    for index, intrinsics in enumerate(intrinsics_sorted):
        current_keyframe_index = (index + 1) * step_size

        if intrinsics is None:
            continue

        animated_obj.data.angle = intrinsics.field_of_view
        animated_obj.data.shift_x = intrinsics.shift_x
        animated_obj.data.shift_y = intrinsics.shift_y

        animated_obj.data.keyframe_insert(
            data_path="lens", index=-1, frame=current_keyframe_index
        )
        animated_obj.data.keyframe_insert(
            data_path="shift_x", index=-1, frame=current_keyframe_index
        )
        animated_obj.data.keyframe_insert(
            data_path="shift_y", index=-1, frame=current_keyframe_index
        )


def add_camera_animation(
    cameras,
    parent_collection,
    animation_frame_source="ORIGINAL",
    number_interpolation_frames=0,
    interpolation_type="LINEAR",
    remove_rotation_discontinuities=True,
):
    """Add an animated camera from a set of reconstructed cameras."""
    if animation_frame_source == "ORIGINAL":
        number_interpolation_frames = 0

    some_cam = cameras[0]
    cam_obj = add_camera_object(
        some_cam, "Animated Camera", parent_collection
    )

    cameras_sorted = sorted(
        cameras,
        key=lambda cam: int("".join(filter(str.isdigit, cam["image_name"])))
    )

    transformations_sorted = []
    camera_intrinsics_sorted = []

    for cam in cameras_sorted:
        matrix_world = compute_camera_matrix_world(cam["position"], cam["rotation"])

        fov = compute_field_of_view(cam)
        shift_x = (cam["cx"] - cam["width"] / 2.0) / cam["width"]
        shift_y = (cam["cy"] - cam["height"] / 2.0) / cam["height"]
        camera_intrinsics = _CameraIntrinsics(fov, shift_x, shift_y)

        transformations_sorted.append(matrix_world)
        camera_intrinsics_sorted.append(camera_intrinsics)

    _add_transformation_animation(
        animated_obj_name=cam_obj.name,
        transformations_sorted=transformations_sorted,
        number_interpolation_frames=number_interpolation_frames,
        interpolation_type=interpolation_type,
        remove_rotation_discontinuities=remove_rotation_discontinuities,
    )

    _add_camera_intrinsics_animation(
        animated_obj_name=cam_obj.name,
        intrinsics_sorted=camera_intrinsics_sorted,
        number_interpolation_frames=number_interpolation_frames,
    )
