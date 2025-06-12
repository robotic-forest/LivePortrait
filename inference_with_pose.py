# coding: utf-8

"""
The entrance of humans
"""

import os
import os.path as osp
import tyro
import subprocess
import time
from src.config.argument_config import ArgumentConfig
from src.config.inference_config import InferenceConfig
from src.config.crop_config import CropConfig
from src.live_portrait_pipeline import LivePortraitPipeline


def partial_fields(target_class, kwargs):
    return target_class(**{k: v for k, v in kwargs.items() if hasattr(target_class, k)})


def fast_check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except:
        return False


def fast_check_args(args: ArgumentConfig):
    if not osp.exists(args.source):
        raise FileNotFoundError(f"source info not found: {args.source}")
    
    if args.pitch is None and args.yaw is None and args.roll is None:
        if not osp.exists(args.driving):
            raise FileNotFoundError(f"driving info not found: {args.driving}")


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


def main():
    # set tyro theme
    tyro.extras.set_accent_color("bright_cyan")
    args = tyro.cli(ArgumentConfig)

    ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg")
    if osp.exists(ffmpeg_dir):
        os.environ["PATH"] += (os.pathsep + ffmpeg_dir)

    if not fast_check_ffmpeg():
        raise ImportError(
            "FFmpeg is not installed. Please install FFmpeg (including ffmpeg and ffprobe) before running this script. https://ffmpeg.org/download.html"
        )

    fast_check_args(args)

    # specify configs for inference
    inference_cfg = partial_fields(InferenceConfig, args.__dict__)
    crop_cfg = partial_fields(CropConfig, args.__dict__)

    timer = Timer()
    live_portrait_pipeline = LivePortraitPipeline(
        inference_cfg=inference_cfg,
        crop_cfg=crop_cfg,
        timer=timer
    )

    # run
    live_portrait_pipeline.execute(args)

    print("Timing Summary:")
    for name, duration in timer.summary().items():
        print(f"- {name}: {duration}")


if __name__ == "__main__":
    main()
