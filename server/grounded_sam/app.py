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

from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gblend_server")


SAM2_CHECKPOINT = "./checkpoints/sam2.1_hiera_large.pt"
SAM2_MODEL_CONFIG = "configs/sam2.1/sam2.1_hiera_l.yaml"
GROUNDING_DINO_CONFIG = "grounding_dino/groundingdino/config/GroundingDINO_SwinT_OGC.py"
GROUNDING_DINO_CHECKPOINT = "gdino_checkpoints/groundingdino_swint_ogc.pth"

SAM1_CHECKPOINT = "./checkpoints/sam_vit_h_4b8939.pth"

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

# --------------------
# Segmentation
# --------------------

def segment_image(image_path, device="cuda"):

    sam = sam_model_registry["vit_h"](checkpoint=SAM1_CHECKPOINT)
    sam.to(device=device)

    mask_generator = SamAutomaticMaskGenerator(sam)

    image_bgr = cv2.imread(str(image_path))
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    masks = mask_generator.generate(image_rgb)

    seg_map = np.zeros_like(image_rgb)
    for mask in masks:
        color = np.random.randint(0, 255, 3, dtype=np.uint8)
        seg_map[mask["segmentation"]] = color

    return seg_map


@app.post("/segment/")
async def segment(image: UploadFile = File(...)):
    """SAM1 Automatic Segmentation API"""
    job_id = str(uuid.uuid4())[:8]
    tmpdir = Path(f"/tmp/gblend_server/{job_id}")
    tmpdir.mkdir(parents=True, exist_ok=True)

    image_path = tmpdir / image.filename

    try:
        with open(image_path, "wb") as f:
            f.write(await image.read())

        seg_map = segment_image(str(image_path), DEVICE)

        out_path = tmpdir / "segment.png"
        cv2.imwrite(str(out_path), seg_map)

        return FileResponse(out_path, media_type="image/png", filename="segment.png")

    except Exception as e:
        logger.error(f"[SAM1] Inference failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
    

# --------------------------------------------------------
# MiDaS Depth Estimation
# --------------------------------------------------------
def estimate_depth(image_path, device="cuda"):
    # Load MiDaS model
    midas = torch.hub.load("intel-isl/MiDaS", "DPT_Large")
    midas.to(device).eval()

    # MiDaS transforms
    transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
    transform = transforms.dpt_transform

    # Load image
    img = cv2.imread(str(image_path))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Preprocess
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

    # Normalize (visualization only)
    depth_norm = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)
    depth_map = depth_norm.astype(np.uint8)

    return depth, depth_map


@app.post("/depth/")
async def depth(image: UploadFile = File(...)):
    """MiDaS Depth Estimation API"""
    job_id = str(uuid.uuid4())[:8]
    tmpdir = Path(f"/tmp/gblend_server/{job_id}")
    tmpdir.mkdir(parents=True, exist_ok=True)

    image_path = tmpdir / image.filename

    try:
        # Save uploaded image
        with open(image_path, "wb") as f:
            f.write(await image.read())

        # Run depth estimation
        depth, depth_map = estimate_depth(str(image_path), DEVICE)

        # Save visualization image
        out_path = tmpdir / "depth.png"
        cv2.imwrite(str(out_path), depth_map)

        return FileResponse(out_path, media_type="image/png", filename="depth.png")

    except Exception as e:
        logger.error(f"[MiDaS] Inference failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
