from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import os
import json
import gzip
import shutil
import torch
import random
import logging
import requests
from transformers import CLIPProcessor, CLIPModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gblend_server")

OBJ_PATHS_URL = "https://huggingface.co/datasets/allenai/objaverse/resolve/main/object-paths.json.gz"
LVIS_URL = "https://huggingface.co/datasets/allenai/objaverse/resolve/main/lvis-annotations.json.gz"

clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", use_safetensors=True)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


app = FastAPI()
@app.get("/download_glb/")
def download_glb(query: str = Query(...)):
    try:
        logger.info(f"[Objaverse] Searching GLB for query: {query}")
        save_path = setup_objaverse("data/objaverse_cache", query)
        return FileResponse(
            save_path,
            media_type="model/gltf-binary",
            filename=os.path.basename(save_path)
        )
    except Exception as e:
        logger.error(f"[Objaverse] Download failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
    

def download_file(url, dest_path):
    print(f"[Objaverse] Downloading: {url}")
    response = requests.get(url)
    response.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(response.content)

def unzip_gz(gz_path, out_path):
    with gzip.open(gz_path, 'rb') as f_in:
        with open(out_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(gz_path)

def ensure_metadata_files_exist(data_dir):
    os.makedirs(data_dir, exist_ok=True)

    obj_path_file = os.path.join(data_dir, "object-paths.json.gz")
    lvis_file = os.path.join(data_dir, "lvis-annotations.json.gz")
    obj_path_json = os.path.join(data_dir, "object-paths.json")
    lvis_json = os.path.join(data_dir, "lvis-annotations.json")

    if not os.path.exists(obj_path_json):
        download_file(OBJ_PATHS_URL, obj_path_file)
        unzip_gz(obj_path_file, obj_path_json)

    if not os.path.exists(lvis_json):
        download_file(LVIS_URL, lvis_file)
        unzip_gz(lvis_file, lvis_json)

def get_random_glb_url_from_query(data_dir, query: str):
    ensure_metadata_files_exist(data_dir)

    lvis_json = os.path.join(data_dir, "lvis-annotations.json")
    obj_path_json = os.path.join(data_dir, "object-paths.json")

    with open(lvis_json, 'r') as f:
        category_to_uids = json.load(f)
    with open(obj_path_json, 'r') as f:
        uid_to_path = json.load(f)

    categories = list(category_to_uids.keys())
    inputs = clip_processor(text=[query] + categories, return_tensors="pt", padding=True)

    with torch.no_grad():
        feats = clip_model.get_text_features(**inputs)

    sims = torch.nn.functional.cosine_similarity(feats[0], feats[1:])
    best_category = categories[sims.argmax().item()]
    uid = random.choice(category_to_uids[best_category])
    url = f"https://huggingface.co/datasets/allenai/objaverse/resolve/main/{uid_to_path[uid]}"
    return url, best_category, uid

def download_glb(save_path, url):
    if os.path.exists(save_path):
        print(f"[INFO] File already exists: {save_path}")
        return save_path

    response = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(response.content)
    print(f"[INFO] Downloaded: {save_path}")
    return save_path

def setup_objaverse(data_dir, query: str):
    url, category, uid = get_random_glb_url_from_query(data_dir, query)

    asset_dir = os.path.join(data_dir, "assets")
    save_dir = os.path.join(asset_dir, category)
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"{uid}.glb")
    return download_glb(save_path, url)