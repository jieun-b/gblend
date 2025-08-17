import bpy
import os
import random
import requests
import tempfile
from PIL import Image
from io import BytesIO
from pathlib import Path

from gblend_addon.core import setup_ground

class GBLEND_OT_scene_align_to_ground(bpy.types.Operator):
    bl_idname = "gblend.align_scene_to_ground"
    bl_label = "Align Scene to Ground"
    bl_description = "Use Grounded SAM to estimate ground plane and align scene automatically"
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        settings = scene.gblend_scene_settings
        obj_name = getattr(settings, "scene_name", "")
        return bool(obj_name and obj_name in bpy.data.objects)
    
    def execute(self, context):
        # Use new property group for data_dir
        paths = context.scene.gblend_project_paths
        settings = context.scene.gblend_scene_settings
        image_dir = Path(getattr(paths, "data_dir", "")) / "images"
        all_images = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))

        if len(all_images) < 3:
            self.report({'ERROR'}, "At least 3 images are required in 'images/' folder.")
            return {'CANCELLED'}

        selected_images = random.sample(all_images, min(5, len(all_images)))

        # Prepare temporary directory to save received masks
        mask_dir = tempfile.mkdtemp(prefix="gblend_masks_")
        print(f"[INFO] Saving received masks to: {mask_dir}")

        mask_dict = {}  # {image_path: mask_path}
        for image_path in selected_images:
            try:
                with open(image_path, "rb") as img_file:
                    response = requests.post(
                        "http://localhost:8001/grounded_sam/",
                        files={"image": (image_path.name, img_file, "image/jpeg")},
                    )
                if response.status_code == 200:
                    # Save mask image
                    mask_image = Image.open(BytesIO(response.content)).convert("L")
                    save_path = os.path.join(mask_dir, image_path.stem + "_mask.png")
                    mask_image.save(save_path)
                    mask_dict[image_path] = save_path
                else:
                    self.report({'WARNING'}, f"Grounded SAM failed on {image_path.name}: {response.text}")
            except Exception as e:
                self.report({'WARNING'}, f"Request failed for {image_path.name}: {e}")

        if not mask_dict:
            self.report({'ERROR'}, "No masks returned from Grounded SAM.")
            return {'CANCELLED'}

        cameras = [
            obj for obj in bpy.data.collections.get("Cameras", []).objects
            if obj.type == 'CAMERA' and obj.name != "Animated Camera"
        ]
        animated_camera = bpy.data.objects.get("Animated Camera")

        try:
            setup_ground(
                cameras=cameras,
                animated_camera=animated_camera,
                obj_name=getattr(settings, "scene_name", ""),
                mask_dict=mask_dict  # {Path: mask_path}
            )
            self.report({'INFO'}, "Ground plane estimated and scene aligned.")
        except Exception as e:
            self.report({'ERROR'}, f"Ground setup failed: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}