import bpy
import random
import requests
import shutil
from PIL import Image
from io import BytesIO
from pathlib import Path

from gblend_addon.core import setup_ground, add_shadow_catcher_ground


class GBLEND_OT_scene_align(bpy.types.Operator):
    """Estimate ground plane using Grounded SAM and align the scene"""
    bl_idname = "gblend.align_scene"
    bl_label = "Align Scene to Ground"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        
        settings = context.scene.gblend_scene_settings
        obj_name = getattr(settings, "scene_name", "")
        return bool(obj_name and obj_name in bpy.data.objects)

    def execute(self, context):
        paths = context.scene.gblend_project_paths
        settings = context.scene.gblend_scene_settings

        image_dir = Path(getattr(paths, "data_dir", "")) / "images"
        all_images = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))

        if len(all_images) < 3:
            self.report({'ERROR'}, "At least 3 images are required in 'images/' folder.")
            return {'CANCELLED'}

        selected_images = random.sample(all_images, min(5, len(all_images)))

        # Output directories
        output_dir = Path(getattr(paths, "output_dir", ""))
        images_out = output_dir / "images"
        masks_out = output_dir / "masks"
        images_out.mkdir(parents=True, exist_ok=True)
        masks_out.mkdir(parents=True, exist_ok=True)

        # Grounded SAM endpoint
        sam_url = getattr(settings, "grounded_sam_url", "http://localhost:8001")

        # Request SAM masks
        mask_dict = {}
        for image_path in selected_images:
            try:
                dst_img = images_out / image_path.name
                if not dst_img.exists():
                    shutil.copy(image_path, dst_img)

                with open(image_path, "rb") as img_file:
                    response = requests.post(
                        f"{sam_url}/grounded_sam/",
                        files={"image": (image_path.name, img_file, "image/jpeg")},
                    )

                if response.status_code == 200:
                    mask_image = Image.open(BytesIO(response.content)).convert("L")
                    save_path = masks_out / f"{image_path.stem}_mask.png"
                    mask_image.save(save_path)
                    mask_dict[dst_img] = save_path
                else:
                    self.report({'WARNING'}, f"SAM failed on {image_path.name}: {response.text}")
            except Exception as e:
                self.report({'WARNING'}, f"Request failed for {image_path.name}: {e}")

        if not mask_dict:
            self.report({'ERROR'}, "No masks returned from Grounded SAM.")
            return {'CANCELLED'}

        # Get camera objects
        cameras = [
            obj for obj in bpy.data.collections.get("Cameras", []).objects
            if obj.type == 'CAMERA'
        ]

        try:
            setup_ground(
                cameras=cameras,
                obj_name=getattr(settings, "scene_name", ""),
                mask_dict=mask_dict,
            )
            add_shadow_catcher_ground(size=100.0, z=0.0)
            self.report({'INFO'}, "Ground plane estimated and scene aligned.")
        except Exception as e:
            self.report({'ERROR'}, f"Ground setup failed: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}
