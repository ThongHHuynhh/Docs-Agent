# Libraries

## Overview

Racer2 V3 bundles three internal libraries:

- camera acquisition and stitching
- AI inference and tracking
- color analysis and buffering

They are embedded in the repository and used directly by the application layer.

## Camera Library

Location:

- [`src/libs/racer2_camera`](../src/libs/racer2_camera)

Primary purpose:

- Basler device discovery
- camera configuration
- line-scan acquisition
- vertical stacking of slices
- horizontal stitching across cameras
- JPEG production for downstream consumers

Key files:

- [`src/libs/racer2_camera/src/config.py`](../src/libs/racer2_camera/src/config.py)
- [`src/libs/racer2_camera/src/line_camera.py`](../src/libs/racer2_camera/src/line_camera.py)

Used by:

- [`src/server/local_camera_runtime.py`](../src/server/local_camera_runtime.py)
- [`src/server/camera_service.py`](../src/server/camera_service.py)

## AI Library

Location:

- [`src/libs/ai`](../src/libs/ai)

Primary purpose:

- AI model selection
- asynchronous model initialization
- live-frame inference
- single-image inference
- annotation overlay generation
- optional tracking integration

Key files:

- [`src/libs/ai/config.py`](../src/libs/ai/config.py)
- [`src/libs/ai/pipeline.py`](../src/libs/ai/pipeline.py)
- [`src/libs/ai/src/models/rfdetr.py`](../src/libs/ai/src/models/rfdetr.py)
- [`src/libs/ai/src/models/yolo.py`](../src/libs/ai/src/models/yolo.py)
- [`src/libs/ai/src/trackers/sort.py`](../src/libs/ai/src/trackers/sort.py)

Runtime selection:

- `AI_MODEL_NAME=rfdetr`
  - RF-DETR path
- any other model name
  - YOLO plus SORT path

Used by:

- [`src/server/app.py`](../src/server/app.py)

## Color Library

Location:

- [`src/libs/color`](../src/libs/color)

Primary purpose:

- per-object color extraction around tracked detections
- rolling object history buffering
- color conversion helpers for RGB, XYZ, Lab, and hex

Key exports:

- `ColorAnalyze`
- `ColorBuffer`
- `rgb_to_xyz`
- `xyz_to_lab`
- `rgb_to_hex`
- `hex_to_rgb`
- `hex_to_lab`

Used by:

- [`src/libs/ai/pipeline.py`](../src/libs/ai/pipeline.py)

## Reuse Notes

These libraries are repo-local modules rather than published packages.

When reusing them elsewhere:

- preserve the current import structure
- carry over the required third-party dependencies
- validate camera or AI runtime assumptions in the new host environment
