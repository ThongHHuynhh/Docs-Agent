# Project Overview

## Purpose

Racer2 V3 is the active AI Core service for line-scan acquisition, frame stitching, live streaming, and optional AI-assisted inspection. It is designed around two Basler line cameras and supports both hardware-backed and hardware-free development workflows.

## Core Capabilities

- dual-camera acquisition and stitched frame generation
- browser-friendly JPEG capture and live WebSocket streaming
- local camera access, remote camera access, and emulated camera generation
- optional RF-DETR or YOLO inference
- tracked-object color analysis with in-memory buffering
- external inference forwarding through `POST /analyze`
- file-driven local inference through `POST /inference`

## Operating Modes

The application can run in three camera modes:

- `local`
  - the main FastAPI service owns Basler access directly
- `remote`
  - the main FastAPI service polls a separate host-side camera service over HTTP
- `emulated`
  - the app generates synthetic frames for debugging and UI validation

AI processing can be:

- disabled, for raw streaming only
- enabled with `rfdetr`
- enabled with YOLO plus SORT by choosing a non-`rfdetr` model name

## High-Level Flow

1. [`main.py`](../main.py) launches the main FastAPI app from [`src/server/app.py`](../src/server/app.py).
2. The app builds a camera runtime based on `CAMERA_MODE`.
3. The runtime begins capturing, polling, or emulating JPEG frames.
4. If AI is enabled, model initialization runs in a background thread and reports checkpoints.
5. The latest frame is served through:
   - `GET /capture`
   - `POST /analyze`
   - `POST /inference`
   - `WebSocket /ws`
6. When color analysis is active, tracked object samples are buffered and exposed through color endpoints.

## Main Components

- `src/server`
  - application lifecycle, endpoints, camera runtime selection, and AI status reporting
- `src/front`
  - browser viewer and health dashboard
- `src/libs/racer2_camera`
  - acquisition, stitching, resizing, and JPEG encoding for the live camera workflow
- `src/libs/ai`
  - RF-DETR or YOLO inference, tracking, annotation, and single-image inference
- `src/libs/color`
  - color conversion, per-object analysis, and rolling sample buffers
- `Docs`
  - operational and technical documentation

## Service Split

Racer2 V3 can run as one process or as two cooperating services:

- main application on port `8000`
- optional dedicated camera service on port `8001`

This split is useful when the camera host must remain close to the Basler runtime while the web or AI layer runs elsewhere.
