# Troubleshooting

## Server Starts But No Frames Arrive

Check:

- `GET /status`
- whether `camera.ready` is `false`
- whether the WebSocket is receiving text such as `warming_up`

If using local mode:

- verify pylon is installed
- verify both Basler cameras are connected
- verify the process can access the cameras

If using remote mode:

- verify `REMOTE_CAMERA_BASE_URL`
- verify the host-side camera service is running
- verify `/capture` on the camera host returns a JPEG

If using emulated mode:

- verify `CAMERA_MODE=emulated`
- verify `EMULATED_CAMERA_IMAGE_PATH` points to a readable file when set

## Camera Busy Or Unavailable

Symptoms:

- `/status` reports camera not ready
- logs mention camera initialization failure or busy hardware

What to check:

- close Pylon Viewer or any other process using the cameras
- confirm no older copy of the service is still running
- restart the host if the driver state appears stuck

## Remote Camera Mode Does Not Refresh

Check:

- `REMOTE_CAMERA_BASE_URL` has no typo
- the camera host exposes port `8001`
- `GET <REMOTE_CAMERA_BASE_URL>/status` returns `200`
- the main app can resolve the host from its own environment

Common causes:

- Docker container cannot reach the host URL being used
- Windows firewall blocks the camera service
- the camera host is up but `/capture` is failing

## WebSocket Stream Shows Text Instead Of Images

This is expected when:

- the camera is warming up
- camera initialization failed
- remote mode has not yet polled a valid frame

The text usually comes from:

- camera status messages
- `warming_up`

## AI Never Becomes Ready

Possible causes:

- invalid Roboflow credentials
- large model initialization time
- unsupported local runtime environment

What to verify:

- `GET /status`
- `.env` contains valid AI credentials
- the selected model in `AI_MODEL_NAME` is intentional

## POST /inference Returns 404

Check:

- `SrcDir` points to a directory on the machine running the main app
- `ImageName` is correct
- the combined path `SrcDir/ImageName` exists

Remember:

- this endpoint reads files locally from disk
- it does not fetch remote URLs

## Color Endpoints Return Empty Data

Possible reasons:

- `DETECTION_AND_TRACK=false`
- the AI model is not ready yet
- no tracked objects have been processed since the last buffer clear
- a previous `GET /color-data` or `POST /color-analysis` call already cleared the buffer

## External Inference Endpoint Fails

Possible causes:

- `INFERENCE_URL` is wrong
- `INFERENCE_API_HEADER` is wrong
- `INFERENCE_API_KEY` is wrong
- the upstream inference service is unavailable

What to verify:

- [`.env`](../.env)
- [`settings.json`](../settings.json)
- network reachability from the machine running the main app

## Pixel Format Problems

Symptoms:

- wrong colors in output frames
- conversion errors during capture
- OpenCV errors involving YUV conversion

What to verify:

- `CAMERA_PIXEL_FORMAT` matches the actual camera output
- `CAMERA_CONFIG_BY_PYLON=true` when external camera configuration owns the format
- `BGR8` is used when the camera already emits OpenCV-ready frames

## General Diagnostic Sequence

1. Call `/status`
2. Confirm `camera.ready`
3. Confirm `/capture` works
4. Confirm the browser page updates
5. If AI is enabled, wait for `ai.phase=ready`
6. Then test `/analyze`, `/inference`, or WebSocket streaming
