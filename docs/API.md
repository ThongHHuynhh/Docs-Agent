# API Reference

## Main Service Base URL

By default the service listens on:

```text
http://localhost:8000
```

The dedicated host-side camera service listens on:

```text
http://localhost:8001
```

## GET /

Returns the HTML frontend from [`src/front/index.html`](../src/front/index.html).

Response:

- `200 text/html`

## GET /status

Returns structured runtime state for:

- AI initialization
- camera readiness
- stream readiness

Example response shape:

```json
{
  "ai": {
    "enabled": true,
    "model_name": "rfdetr",
    "phase": "ready",
    "message": "RFDETR ready",
    "error": null,
    "checkpoints": []
  },
  "camera": {
    "ready": true,
    "message": "Camera ready",
    "error": null,
    "backend": "local"
  },
  "stream": {
    "has_frame": true,
    "mode": "tracked"
  }
}
```

Response:

- `200 application/json`

## GET /capture

Returns the latest JPEG frame from the shared frame cache.

Success:

- `200 image/jpeg`

Failure cases:

- `503` if the camera is not ready
- `503` if no frame has been produced yet

## POST /analyze

Forwards the latest frame to the external inference service defined by `INFERENCE_URL`.

Behavior:

- sends the frame as multipart form data
- includes the configured API header if one is present
- retries on `429`

Success:

- `200 application/json`

Failure cases:

- `503` if camera is unavailable
- `503` if no frame is available
- `429` if the inference service remains at capacity after retries
- `400` or `503` if returned by the upstream inference service

## GET /camera/alignment

Returns the current stitching alignment values.

Response shape:

```json
{
  "h_offset": 10,
  "v_offset": 190,
  "num_images": 5,
  "backend": "local"
}
```

Response:

- `200 application/json`
- `503 application/json` if the camera runtime is not initialized or alignment cannot be read

## POST /camera/alignment

Updates stitch alignment settings and resets the stacked frame buffer.

Request body:

```json
{
  "h_offset": 10,
  "v_offset": 190,
  "num_images": 5
}
```

`num_images` is optional and must be at least `1` when provided.

Response shape:

```json
{
  "h_offset": 10,
  "v_offset": 190,
  "num_images": 5,
  "backend": "local",
  "buffer_reset": true
}
```

Response:

- `200 application/json`
- `503 application/json` if the camera runtime is not initialized or alignment cannot be updated

## GET /color-data

Returns the current color analysis buffer and then clears it.

Response shape:

```json
{
  "objects": [
    {
      "id": 1,
      "latest": {},
      "history": []
    }
  ]
}
```

When detection/tracking is disabled or the AI model is not ready, `objects` is empty.

## POST /inference

Runs local AI inference for an image on disk.

Request body:

```json
{
  "feature_name": "inspection",
  "ImageName": "sample.jpg",
  "SrcDir": "D:/data/job_001",
  "Timestamp": "2026-05-12T13:00:00"
}
```

Behavior:

- reads `SrcDir/ImageName`
- creates `SrcDir/Inference_Images/` when missing
- runs local AI inference through the configured pipeline
- writes an annotated file named `inferenced_<ImageName>`
- returns product-shaped color-analysis output

Success response shape:

```json
{
  "Data": {
    "Products": []
  },
  "Detected": false,
  "Inference_image_path": "D:/data/job_001/Inference_Images/inferenced_sample.jpg",
  "image_name": "sample.jpg"
}
```

Failure cases:

- `404` when the source image does not exist
- `503` when the AI model is still loading

## POST /color-analysis

Returns the current contents of the color analysis buffer and then clears the buffer.

Response shape:

```json
{
  "Products": [
    {
      "ID": 1,
      "color_sample": {
        "opening": "square",
        "size": "10x10",
        "positions": [
          {
            "xc": 567,
            "yc": 412
          }
        ]
      },
      "confidence": 0.818303,
      "color_analysis": {
        "RGB": [130, 225, 79],
        "LChannel": 78.9,
        "CIELAB": [78.9, 42.5, 6.2]
      }
    }
  ]
}
```

Response:

- `200 application/json`

## GET /export_color_csv

Exports the current color buffer as CSV.

Response:

- `200 text/csv`
- `Content-Disposition: attachment; filename=color_data.csv`

## GET /delete_all_color_buffer

Clears all buffered color analysis samples.

Response:

- `200 text/plain`

## GET /delete_color_buffer/{obj_id}

Clears buffered color analysis samples for a single tracked object ID.

Response:

- `200 text/plain`

## WebSocket /ws

Streams either:

- raw JPEG frames
- AI-annotated JPEG frames

The server sends text messages in non-frame conditions:

- `warming_up`
- camera error text

## AI Checkpoints

The current AI checkpoint keys exposed through `/status` are:

- `pipeline`
- `providers`
- `weights`
- `tracker`
- `ready`

Each checkpoint includes:

- `key`
- `label`
- `state`
- `message`

States currently used:

- `pending`
- `active`
- `done`
- `error`

## Host Camera Service API

The service started by [`camera_main.py`](../camera_main.py) provides a camera-only API on port `8001`.

### GET /status

Returns:

```json
{
  "camera": {
    "ready": true,
    "message": "Camera ready",
    "error": null,
    "backend": "local"
  },
  "stream": {
    "has_frame": true,
    "mode": "raw"
  }
}
```

### GET /camera/alignment

Returns the camera-side stitch alignment state.

### POST /camera/alignment

Updates camera-side stitch offsets and optional `num_images`.

### GET /capture

Returns the latest raw JPEG frame from the camera-side service.

### WebSocket /ws

Streams raw JPEG frames from the camera-side service.
