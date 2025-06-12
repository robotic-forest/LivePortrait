#!/bin/bash

# Ensure the script is run from the correct directory
cd "$(dirname "$0")"

# Set the path to the cuDNN libraries required by onnxruntime-gpu
# This path is specific to your 'LivePortrait' conda environment
CUDNN_LIB_PATH="/home/xolochu/miniconda3/envs/LivePortrait/lib/python3.10/site-packages/nvidia/cudnn/lib"
export LD_LIBRARY_PATH="${CUDNN_LIB_PATH}:${LD_LIBRARY_PATH}"

# --- Execution Mode ---
# Set to true to force CPU execution, false to use GPU (if available)
FORCE_CPU=true

# --- Animation Parameters ---
# You can easily change these values

# Input source image
SOURCE_IMAGE="assets/examples/source/s0.jpg"

# Output directory for the animation
OUTPUT_DIR="animations/"

# Head pose angles
PITCH="10"
YAW="-10"
ROLL="5"


# --- Build and Execute the Command ---

# Conditionally add the --flag_force_cpu argument
CPU_FLAG=""
if [ "$FORCE_CPU" = true ]; then
    echo "Forcing CPU execution."
    CPU_FLAG="--flag_force_cpu"
else
    echo "Using GPU for execution."
fi

echo "Running LivePortrait inference..."

python inference_with_pose.py \
    -s "$SOURCE_IMAGE" \
    -o "$OUTPUT_DIR" \
    --pitch "$PITCH" \
    --yaw "$YAW" \
    --roll "$ROLL" \
    $CPU_FLAG

echo "Animation saved to the '${OUTPUT_DIR}' directory."
echo "run.sh finished." 