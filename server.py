import os
# Set the current working directory to the script's directory
# to ensure relative paths in the LivePortraitPipeline work correctly.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import tyro
import time

from src.config.argument_config import ArgumentConfig
from src.config.inference_config import InferenceConfig
from src.config.crop_config import CropConfig
from src.live_portrait_pipeline import LivePortraitPipeline

# --- Helper Functions ---
def partial_fields(target_class, kwargs):
    return target_class(**{k: v for k, v in kwargs.items() if hasattr(target_class, k)})

class Timer:
    def __init__(self):
        self.reset()

    def tic(self, name):
        self.starts[name] = time.perf_counter()

    def toc(self, name):
        if name in self.starts:
            self.timings[name] = time.perf_counter() - self.starts[name]

    def reset(self):
        self.timings = {}
        self.starts = {}

    def summary(self):
        return {k: f"{v:.6f}s" for k, v in self.timings.items()}

# --- FastAPI App ---
app = FastAPI()

# --- Global Model Pipeline ---
live_portrait_pipeline: LivePortraitPipeline = None
argument_config: ArgumentConfig = None

@app.on_event("startup")
async def startup_event():
    """
    Load the model on server startup.
    """
    global live_portrait_pipeline
    global argument_config

    # Arguments are now parsed from the command line when server.py is launched.
    # See run_server.sh for an example.
    args = tyro.cli(ArgumentConfig)
    
    inference_cfg = partial_fields(InferenceConfig, args.__dict__)
    crop_cfg = partial_fields(CropConfig, args.__dict__)

    timer = Timer()
    live_portrait_pipeline = LivePortraitPipeline(
        inference_cfg=inference_cfg,
        crop_cfg=crop_cfg,
        timer=timer
    )
    argument_config = args
    print("LivePortraitPipeline loaded successfully.")

class InferenceRequest(BaseModel):
    source_image: str
    pitch: float
    yaw: float
    roll: float
    output_dir: str = "animations/"

@app.post("/inference/")
async def inference(request: InferenceRequest):
    if not live_portrait_pipeline:
        raise HTTPException(status_code=503, detail="Model is not loaded yet.")
    
    # Create a copy of the base arguments and update with request data
    args = ArgumentConfig(**argument_config.__dict__)
    args.source = os.path.abspath(request.source_image)
    args.pitch = request.pitch
    args.yaw = request.yaw
    args.roll = request.roll
    args.output_dir = request.output_dir
    # args.driving = None # DO NOT set driving to None. The pipeline expects a default path, even when using pose.
    
    if not os.path.exists(args.source):
        raise HTTPException(status_code=400, detail=f"Source image not found: {args.source}")

    try:
        live_portrait_pipeline.timer.reset()
        live_portrait_pipeline.execute(args)
        
        timings = live_portrait_pipeline.timer.summary()
        output_path = os.path.join(request.output_dir, os.path.basename(request.source_image).replace('.jpg', '.mp4'))
        
        return {
            "message": "Inference completed successfully.",
            "output_path": output_path,
            "timings": timings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 