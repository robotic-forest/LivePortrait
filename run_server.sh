#!/bin/bash

# --- Execution Mode ---
# Set to true to force CPU execution, false to use GPU (if available)
FORCE_CPU=true

# Ensure the script is run from its own directory
cd "$(dirname "$0")"

# Set the path to the cuDNN libraries required by onnxruntime-gpu
# This path is specific to your 'LivePortrait' conda environment.
CUDNN_LIB_PATH="/home/xolochu/miniconda3/envs/LivePortrait/lib/python3.10/site-packages/nvidia/cudnn/lib"
export LD_LIBRARY_PATH="${CUDNN_LIB_PATH}:${LD_LIBRARY_PATH}"

echo "Starting FastAPI server for LivePortrait..."
echo "LD_LIBRARY_PATH is set to: $LD_LIBRARY_PATH"

# Conditionally set the arguments for python
if [ "$FORCE_CPU" = true ]; then
    echo "Forcing CPU execution."
    DEVICE_ARGS="--flag_force_cpu"
else
    echo "Using GPU for execution."
    DEVICE_ARGS="--device_id 0"
fi

# Run the server with the configured device arguments
python server.py $DEVICE_ARGS 