import os
import bpy
import json

from .animate import add_camera_animation
from .utils import add_camera_object, load_background_image
from ..utils import add_collection

def add_cameras(cam_dicts, parent_collection, add_background_images=False, camera_collection_name="Cameras"):
    camera_collection = add_collection(camera_collection_name, parent_collection)

    for cam_data in cam_dicts:
        cam_obj = add_camera_object(cam_data, cam_data["name"], camera_collection)

        if add_background_images:
            img_path = cam_data["image_path"]
            if os.path.exists(img_path):
                bg_image = bpy.data.images.load(img_path)
                load_background_image(bg_image, cam_obj)


def setup_cameras(json_path, image_dir, parent_collection):
    with open(json_path, 'r') as f:
        camera_data = json.load(f)

    cam_dicts = []
    for data in camera_data:
        cam_dict = {
            "name": os.path.splitext(data["img_name"])[0] + "_cam",
            "image_name": data["img_name"],
            "image_path": os.path.join(image_dir, data["img_name"]),
            "width": data["width"],
            "height": data["height"],
            "fx": data["fx"],
            "fy": data["fy"],
            "cx": data.get("cx", data["width"] / 2.0),
            "cy": data.get("cy", data["height"] / 2.0),
            "rotation": data["rotation"],
            "position": data["position"],
        }
        cam_dicts.append(cam_dict)

    scene_settings = bpy.context.scene.gblend_scene_settings
    if scene_settings.frame_end == 0:
        scene_settings.frame_end = len(cam_dicts)
        
    add_cameras(cam_dicts, parent_collection, add_background_images=True)


def setup_animated_camera(cameras, animated_camera=None):
    scene_settings = bpy.context.scene.gblend_scene_settings
    stride = scene_settings.stride
    frame_start = scene_settings.frame_start
    frame_end = scene_settings.frame_end
    number_interpolation_frames = scene_settings.interpolation_frames

    filtered_cameras = [
        cam for i, cam in enumerate(cameras)
        if frame_start <= (i + 1) <= frame_end  # 1-based index
    ]

    sampled_cameras = [cam for i, cam in enumerate(filtered_cameras) if i % stride == 0]

    add_camera_animation(sampled_cameras, animated_camera, number_interpolation_frames=number_interpolation_frames)

    animated_camera = bpy.data.objects.get("Animated Camera")
    if animated_camera:
        bpy.context.scene.camera = animated_camera