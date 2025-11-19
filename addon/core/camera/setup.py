import os
import bpy
import json

from .animate import add_camera_animation
from .utils import add_camera_object, load_background_image, compute_camera_path
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
        
    add_cameras(cam_dicts, parent_collection, add_background_images=True)


def setup_animated_camera(cameras, parent_collection):
    settings = bpy.context.scene.settings
    number_interpolation_frames = settings.interpolation_frames

    start_name = settings.start_camera
    end_name = settings.end_camera

    if not (start_name and end_name):
        print("[ERROR] Start or End camera not set.")
        return None

    start_cam = bpy.data.objects.get(start_name)
    end_cam = bpy.data.objects.get(end_name)

    if not start_cam or not end_cam:
        print(f"[ERROR] Could not find cameras: {start_name}, {end_name}")
        return None

    path_cameras = compute_camera_path(
        start_cam, end_cam, number_interpolation_frames=number_interpolation_frames, parent_collection=parent_collection
    )

    animated_camera = add_camera_animation(
        path_cameras,
    )

    if animated_camera:
        bpy.context.scene.camera = animated_camera
        print(f"[INFO] Animated Camera generated from {start_name} → {end_name} "
              f"with {len(path_cameras)} keyframes.")

    return animated_camera
