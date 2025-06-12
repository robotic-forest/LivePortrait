# Live Portrait FastAPI Server

This document provides instructions on how to set up and run the FastAPI server for Live Portrait inference.

The server preloads the model on startup to provide fast inference times, similar to the ComfyUI node.

## 1. Setup

First, ensure you have all the necessary Python dependencies installed. Navigate to the `LivePortrait/LivePortrait` directory and run:

```bash
pip install -r requirements.txt
```

This will install `fastapi`, `uvicorn`, and all other required packages.

## 2. Running the Server

To start the server, make the `run_server.sh` script executable and then run it:

```bash
chmod +x run_server.sh
./run_server.sh
```

The script will handle setting the necessary `LD_LIBRARY_PATH` environment variable and then start the Python server. You should see output indicating that the server is running and that the `LivePortraitPipeline` has been loaded successfully. By default, the server runs on `http://0.0.0.0:8000`.

### GPU/CPU Configuration

To switch between GPU and CPU execution, you can now simply edit the `FORCE_CPU` variable at the top of the `run_server.sh` script.

-   **To use the GPU**, set `FORCE_CPU=false`.
-   **To use the CPU**, set `FORCE_CPU=true`.

The script will automatically pass the correct arguments to the Python server based on this setting. If you need to use a specific GPU other than device 0, you can modify the `DEVICE_ARGS` for the GPU case within the script.

## 3. API Usage

The server exposes an `/inference/` endpoint that accepts `POST` requests.

### Request Body

The request body should be a JSON object with the following fields:

-   `source_image` (string, required): The path to the source image.
-   `pitch` (float, required): The head pitch angle.
-   `yaw` (float, required): The head yaw angle.
-   `roll` (float, required): The head roll angle.
-   `output_dir` (string, optional): The directory to save the output animation. Defaults to `"animations/"`.

### Example `curl` Request

You can use a tool like `curl` to send a request:

```bash
curl -X POST "http://127.0.0.1:8000/inference/" \
     -H "Content-Type: application/json" \
     -d '{
           "source_image": "assets/examples/source/s0.jpg",
           "pitch": 10,
           "yaw": -10,
           "roll": 5
         }'
```

### Example Success Response

A successful request will return a JSON object with the output path and timing information:

```json
{
  "message": "Inference completed successfully.",
  "output_path": "animations/s0.mp4",
  "timings": {
    "prepare_source": "0.123456s",
    "driving_video_preparation": "0.000000s",
    "live_portrait_wrapper": "1.234567s",
    "video_post_processing": "0.012345s"
  }
}
``` 