import torch
import cv2
import numpy as np
from pathlib import Path
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

# --------------------
# Depth Estimation (MiDaS Large)
# --------------------
def estimate_depth(image_path, device="cuda"):
    midas = torch.hub.load("intel-isl/MiDaS", "DPT_Large")
    midas.to(device).eval()

    transform = torch.hub.load("intel-isl/MiDaS", "transforms").dpt_transform
    img = cv2.imread(str(image_path))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    input_batch = transform(img_rgb).to(device)
    with torch.no_grad():
        prediction = midas(input_batch)
        depth = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()
    depth = depth.cpu().numpy().astype(np.float32)

    # depth normalization (for visualization only)
    depth_norm = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)
    depth_map = depth_norm.astype(np.uint8)
    return depth, depth_map


# --------------------
# Segmentation (SAM)
# --------------------
def segment_image(image_path, device="cuda"):
    sam_checkpoint = "./checkpoints/sam_vit_h_4b8939.pth"
    model_type = "vit_h"

    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    sam.to(device=device)

    # 필요 시 min_area, pred_iou_thresh 조정 가능
    mask_generator = SamAutomaticMaskGenerator(sam)

    image_bgr = cv2.imread(str(image_path))
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    masks = mask_generator.generate(image_rgb)

    seg_map = np.zeros_like(image_rgb)
    for i, mask in enumerate(masks):
        color = np.random.randint(0, 255, 3, dtype=np.uint8)
        seg_map[mask["segmentation"]] = color
    return seg_map