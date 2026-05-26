# Configuration

## Configuration Sources

The project uses two kinds of configuration:

- non-secret runtime settings
  - stored in [`settings.json`](../settings.json)
- secrets and environment selection
  - stored in [`.env`](../.env) and optionally [`.env.debug`](../.env.debug)

The loader lives in [`src/settings.py`](../src/settings.py).

## Loading Order

The loader resolves configuration in this order:

1. `.env`
2. if `APP_ENV_FILE` is set, that file is loaded on top of `.env`
3. otherwise `.env.debug` is loaded when `APP_ENV=debug`
4. `settings.json` is loaded after the environment files
5. when a setting exists in both places, the environment value wins over `settings.json`

In practice:

- secrets normally live in `.env`
- profile-specific non-secrets normally live in `settings.json`
- environment variables can override both when needed

## settings.json

[`settings.json`](../settings.json) supports profile sections:

- `production`
- `debug`
- `docker`

Supported keys currently used by the app:

### Stream

- `STREAM_DELAY_S`
  - delay between WebSocket iterations

### External Inference

- `INFERENCE_URL`
- `INFERENCE_RETRIES`
- `INFERENCE_RETRY_DELAY_S`

### Camera Runtime

- `CAMERA_MODE`
  - `local` initializes Basler cameras in the web app process
  - `remote` polls a separate camera service over HTTP
  - `emulated` generates synthetic JPEG frames in-process for UI and API testing
- `CAMERA_WHITE_BALANCE`
  - enables one-shot white balance after acquisition starts
- `CAMERA_TRIGGER_SOURCE`
  - default: `Line2`
- `CAMERA_TRIGGER_ACTIVATION`
  - default: `RisingEdge`
- `CAMERA_TRIGGER_SELECTOR`
  - default: `LineStart`
- `CAMERA_TRIGGER_MODE`
  - boolean runtime setting; `true` writes `TriggerMode=On`, `false` writes `TriggerMode=Off`
- `CAMERA_PIXEL_FORMAT`
  - supported by the current conversion path: `BGR8`, `BGR8Packed`, `YCbCr422_8`, `YUV422Packed`, `YUV422_YUYV_Packed`
  - `BGR8` and `BGR8Packed` are treated as OpenCV-ready BGR images
  - YUV422 formats are converted with `cv2.COLOR_YUV2BGR_YUY2`
- `CAMERA_CONFIG_BY_PYLON`
  - when `true`, the app skips its own camera feature writes and uses the camera state configured outside the app
- `REMOTE_CAMERA_BASE_URL`
- `REMOTE_CAMERA_TIMEOUT_S`
- `REMOTE_CAMERA_POLL_INTERVAL_S`
- `EMULATED_CAMERA_WIDTH`
- `EMULATED_CAMERA_HEIGHT`
- `EMULATED_CAMERA_FPS`
- `EMULATED_CAMERA_JPEG_QUALITY`
- `EMULATED_CAMERA_IMAGE_PATH`
  - optional image file used by the emulated runtime instead of generated frames

### AI Runtime

- `DETECTION_AND_TRACK`
- `AI_MODEL_NAME`
- `YOLO_MODEL_PATH`
- `RFDETR_CONF_THRESH`
- `CORE_MODEL_SAM_ENABLED`
- `CORE_MODEL_SAM3_ENABLED`
- `CORE_MODEL_GAZE_ENABLED`

## .env Files

The current secret-bearing keys are:

- `INFERENCE_API_HEADER`
- `INFERENCE_API_KEY`
- `RFDETR_MODEL_ID`
- `ROBOFLOW_API_KEY`

Example:

```env
INFERENCE_API_HEADER=X-API-Key
INFERENCE_API_KEY=replace-me
RFDETR_MODEL_ID=your-project/your-version
ROBOFLOW_API_KEY=replace-me
```

Useful runtime selectors:

```env
APP_ENV=debug
APP_ENV_FILE=.env.debug
```

## Runtime Settings Object

The app exposes all resolved configuration through [`src/settings.py`](../src/settings.py) as a `settings` object.

That object is consumed by:

- [`src/server/app.py`](../src/server/app.py)
- [`src/server/camera_service.py`](../src/server/camera_service.py)
- runtime-specific camera modules under [`src/server`](../src/server)

## Camera Library Config

The camera library has its own typed config in [`src/libs/racer2_camera/src/config.py`](../src/libs/racer2_camera/src/config.py).

Important fields:

- `num_cameras`
- `num_images`
- `max_stack`
- `pixels_per_shot`
- `h_offset`
- `v_offset`
- `exposure_time_us`
- `pixel_format`
- `trigger_source`
- `trigger_activation`
- `trigger_selector`
- `trigger_mode`
- `packet_size`
- `inter_packet_delay`
- `jpeg_quality`
- `store_images`
- `output_path`
- `white_balance`
- `is_config_by_pylon`
- `zoom_factor`
- `grab_timeout_ms`

Most of these are currently set in code when the app constructs `Racer2CameraConfig`.
`white_balance`, `pixel_format`, trigger settings, and `is_config_by_pylon` are controlled by `CAMERA_*` keys in `settings.json` or the environment.

### Camera Pixel Format

Use `CAMERA_PIXEL_FORMAT` to choose how camera buffers are interpreted after stitching:

```json
"CAMERA_PIXEL_FORMAT": "BGR8"
```

`BGR8` and `BGR8Packed` skip color conversion because pypylon returns frames in OpenCV channel order. Use this when the camera is configured for BGR output.

```json
"CAMERA_PIXEL_FORMAT": "YCbCr422_8"
```

`YCbCr422_8` and supported YUV422 aliases are converted to BGR before resize, JPEG encoding, streaming, and AI processing.

### Pylon-Managed Camera Config

Set `CAMERA_CONFIG_BY_PYLON` to `true` when camera features are configured in Pylon Viewer or another pylon workflow and the app should not write pixel format, exposure, trigger, packet size, or height values during startup.

```json
"CAMERA_CONFIG_BY_PYLON": true
```

When this value is `false`, the app writes camera features from `Racer2CameraConfig` during startup.

## AI Library Config

The AI library config lives in [`src/libs/ai/config.py`](../src/libs/ai/config.py).

Important fields:

- `model_name`
- `yolo_model_path`
- `rfdetr_model_id`
- `roboflow_api_key`
- `rfdetr_conf_thresh`
- `core_model_sam_enabled`
- `core_model_sam3_enabled`
- `core_model_gaze_enabled`
- `color_analyze_enabled`

Current application behavior always enables `color_analyze_enabled` inside the AI config used by the main app.

### Camera Mode

`CAMERA_MODE` supports:

- `local`
  - FastAPI app initializes Basler cameras directly through `pypylon`
- `remote`
  - FastAPI app polls a separate camera service over HTTP
- `emulated`
  - FastAPI app generates synthetic frames without requiring physical cameras

When `CAMERA_MODE=remote`, the app expects:

- `REMOTE_CAMERA_BASE_URL`
- `REMOTE_CAMERA_TIMEOUT_S`
- `REMOTE_CAMERA_POLL_INTERVAL_S`

When `CAMERA_MODE=emulated`, the app can use:

- generated frames based on width, height, and fps
- an optional source image from `EMULATED_CAMERA_IMAGE_PATH`

## Recommended Practice

- Keep secrets only in `.env` files.
- Keep environment-specific but non-secret settings in `settings.json`.
- Use `APP_ENV=debug` for debug mode rather than editing production values in place.
- Use the `docker` profile only for the container-facing settings that differ from local or production host operation.
