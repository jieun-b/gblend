import sys
import os

# Grounded-SAM-2 절대경로 지정
ROOT_DIR = "/home/Grounded-SAM-2"
sys.path.insert(0, ROOT_DIR)

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import cv2
import uuid
import torch
import logging
import numpy as np
from pathlib import Path
from torchvision.ops import box_convert

from grounding_dino.groundingdino.util.inference import load_model, load_image, predict
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gblend_server")

# app.py (grounded_sam)
MODEL_ROOT = os.environ.get("MODEL_ROOT", "/home/Grounded-SAM-2")

SAM2_CHECKPOINT = os.path.join(MODEL_ROOT, "checkpoints/sam2.1_hiera_large.pt")
GROUNDING_DINO_CONFIG = os.path.join(MODEL_ROOT, "grounding_dino/groundingdino/config/GroundingDINO_SwinT_OGC.py")
GROUNDING_DINO_CHECKPOINT = os.path.join(MODEL_ROOT, "gdino_checkpoints/groundingdino_swint_ogc.pth")

BOX_THRESHOLD = 0.35
TEXT_THRESHOLD = 0.25
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

app = FastAPI()

@app.post("/grounded_sam/")
async def grounded_sam_predict(image: UploadFile = File(...)):
    job_id = str(uuid.uuid4())[:8]
    tmpdir = Path(f"/tmp/gblend_server/{job_id}")
    tmpdir.mkdir(parents=True, exist_ok=True)

    image_path = tmpdir / image.filename
    try:
        with open(image_path, "wb") as f:
            f.write(await image.read())

        mask_path = grounded_sam_floor(str(image_path), tmpdir)
        return FileResponse(mask_path, media_type="image/png", filename="mask.png")

    except Exception as e:
        logger.error(f"[GroundedSAM] Inference failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
    

def grounded_sam_floor(image_path, save_dir):
    sam2_model = build_sam2(SAM2_MODEL_CONFIG, SAM2_CHECKPOINT, device=DEVICE)
    sam2_predictor = SAM2ImagePredictor(sam2_model)
    grounding_model = load_model(
        model_config_path=GROUNDING_DINO_CONFIG,
        model_checkpoint_path=GROUNDING_DINO_CHECKPOINT,
        device=DEVICE
    )

    image_source, image = load_image(image_path)
    sam2_predictor.set_image(image_source)
    h, w, _ = image_source.shape

    caption = "floor, ground, ground plane, floor surface"
    boxes, confidences, labels = predict(
        model=grounding_model,
        image=image,
        caption=caption,
        box_threshold=BOX_THRESHOLD,
        text_threshold=TEXT_THRESHOLD,
        device=DEVICE
    )

    if boxes.shape[0] == 0:
        raise ValueError("No floor-like region detected")

    boxes = boxes * torch.Tensor([w, h, w, h])
    input_boxes = box_convert(boxes=boxes, in_fmt="cxcywh", out_fmt="xyxy").numpy()

    with torch.autocast(device_type=DEVICE, dtype=torch.bfloat16):
        masks, scores, logits = sam2_predictor.predict(
            point_coords=None,
            point_labels=None,
            box=input_boxes,
            multimask_output=False,
        )

    masks = masks.squeeze(1) if masks.ndim == 4 else masks
    idx = int(np.argmax(scores))
    mask = (masks[idx] * 255).astype(np.uint8)

    ys, xs = np.where(mask > 127)
    if len(ys) == 0:
        raise ValueError("Empty mask from SAM")

    center_y = np.median(ys)
    if center_y < h * 0.5:
        raise ValueError("Mask too high in image (likely wall/ceiling)")

    area_ratio = (mask > 127).sum() / (h * w)
    if area_ratio < 0.01:
        raise ValueError("Mask area too small for floor candidate")

    min_x, max_x = xs.min(), xs.max()
    min_y, max_y = ys.min(), ys.max()
    bbox_w, bbox_h = max_x - min_x, max_y - min_y
    if bbox_h > bbox_w:
        raise ValueError("Mask looks vertical (likely a wall)")
    
    mask_path = os.path.join(save_dir, "mask.png")
    cv2.imwrite(mask_path, mask)
    logger.info(f"[GroundedSAM] Mask saved: {mask_path}")
    return mask_path
