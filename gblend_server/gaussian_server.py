from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import os, uuid, zipfile, shutil, subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gblend_server")

app = FastAPI()
@app.post("/gaussian/")
async def gaussian_generate(data: UploadFile = File(...)):
    job_id = str(uuid.uuid4())[:8]
    work_dir = f"/tmp/gblend_server/{job_id}"
    os.makedirs(work_dir, exist_ok=True)

    zip_path = os.path.join(work_dir, "input.zip")
    with open(zip_path, "wb") as f:
        f.write(await data.read())

    dataset_dir = os.path.join(work_dir, "dataset")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(dataset_dir)

    output_dir = os.path.join(work_dir, "output")
    try:
        subprocess.run([
            "python", "train.py",
            "-s", dataset_dir,
            "-m", output_dir,
            "--iterations", "30000"
        ], check=True, cwd="gaussian-splatting")
    except subprocess.CalledProcessError as e:
        logger.error(f"[Training] Failed: {e}")
        return JSONResponse(status_code=500, content={"error": f"Training failed: {e}"})

    zip_out_path = os.path.join(work_dir, "output.zip")
    shutil.make_archive(zip_out_path.replace(".zip", ""), 'zip', output_dir)

    return FileResponse(zip_out_path, media_type="application/zip", filename="output.zip")