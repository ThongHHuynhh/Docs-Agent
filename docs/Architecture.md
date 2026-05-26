# Architecture

## Runtime Layers

The system is split into three layers:

1. entrypoints
   - [`main.py`](../main.py) launches the main application on port `8000`
   - [`camera_main.py`](../camera_main.py) launches the dedicated camera service on port `8001`
2. server layer
   - [`src/server/app.py`](../src/server/app.py) exposes the main UI, streaming, AI, and color endpoints
   - [`src/server/camera_service.py`](../src/server/camera_service.py) exposes the host-side camera-only API
3. library layer
   - [`src/libs/racer2_camera`](../src/libs/racer2_camera)
   - [`src/libs/ai`](../src/libs/ai)
   - [`src/libs/color`](../src/libs/color)

## Camera Runtime Selection

The main app builds its camera runtime in [`src/server/app.py`](../src/server/app.py):

- `local`
  - uses [`src/server/local_camera_runtime.py`](../src/server/local_camera_runtime.py)
  - Basler access stays inside the main app process
- `remote`
  - uses [`src/server/remote_camera_runtime.py`](../src/server/remote_camera_runtime.py)
  - frames and alignment data are fetched from the separate camera service
- `emulated`
  - uses [`src/server/emulated_camera_runtime.py`](../src/server/emulated_camera_runtime.py)
  - synthetic frames are generated in-process for development and testing

The dedicated camera service supports only:

- `local`
- `emulated`

It does not host AI features.

## Camera Pipeline

The live acquisition pipeline lives in [`src/libs/racer2_camera/src/line_camera.py`](../src/libs/racer2_camera/src/line_camera.py).

High-level flow:

1. discover Basler devices through `pypylon`
2. require the configured number of cameras
3. configure trigger, pixel format, and optional white balance unless `CAMERA_CONFIG_BY_PYLON=true`
4. read `num_images` strips from each camera
5. stack strips vertically per camera
6. apply horizontal and vertical offsets
7. stitch the camera outputs into one image
8. convert the frame to BGR when the selected pixel format requires it
9. resize and JPEG-encode the final output
10. cache the latest JPEG for HTTP and WebSocket consumers

Runtime alignment changes are exposed through:

- `GET /camera/alignment`
- `POST /camera/alignment`

## Remote Camera Flow

[`src/server/remote_camera_runtime.py`](../src/server/remote_camera_runtime.py) continuously polls:

- `/status`
- `/capture`
- `/camera/alignment`

from `REMOTE_CAMERA_BASE_URL`.

This allows a deployment where:

- the camera host keeps direct access to Basler hardware
- the main app consumes frames over HTTP
- the web and AI stack can be deployed separately

## AI Pipeline

The AI orchestration lives in [`src/libs/ai/pipeline.py`](../src/libs/ai/pipeline.py).

The selected model is controlled by `AI_MODEL_NAME`:

- `rfdetr`
  - RF-DETR-backed detection and tracked annotation
- any other value
  - YOLO detection plus SORT tracking

Important behavior:

- AI initialization runs asynchronously so server startup is not blocked
- `/status` exposes AI checkpoint progress
- the WebSocket stream sends raw frames until AI becomes ready
- `run_single_image_inference()` powers the file-based `POST /inference` endpoint

### Color Analysis

The AI pipeline also owns a `ColorBuffer` with recent tracked-object history.

Color features include:

- per-object latest sample state
- rolling per-object history
- CSV export
- product-shaped color-analysis output for downstream consumers

## Data Consumers

The latest frame can be consumed by:

- `GET /capture`
- `POST /analyze`
- `POST /inference`
- `WebSocket /ws`
- the browser UI in [`src/front/index.html`](../src/front/index.html)

## Failure Handling

The service is intentionally soft-failing:

- startup continues even if cameras are unavailable
- `/status` remains available when capture fails
- `/capture`, `/analyze`, and `/inference` return structured errors when needed
- WebSocket clients receive text statuses such as `warming_up` or camera error text instead of a server crash
