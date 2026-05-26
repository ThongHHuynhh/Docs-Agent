# Deployment

## Baseline Setup

Before any deployment:

- create a virtual environment
- install dependencies from `requirements.txt`
- create `.env` from `.env.example`
- review `settings.json`
- confirm the intended profile: `production`, `debug`, or `docker`

## Option 1: Single-Process Local Deployment

Use this when the same Windows machine has direct access to the Basler cameras.

```powershell
python .\main.py
```

Recommended settings:

- `CAMERA_MODE=local`
- `DETECTION_AND_TRACK=true` or `false` depending on workload

This is the simplest production shape when:

- pylon is installed locally
- the host should serve both frames and AI responses
- network separation is not required

## Option 2: Debug or Hardware-Free Deployment

Use this when testing UI, APIs, or AI flow without cameras.

```powershell
$env:APP_ENV="debug"
python .\main.py
```

Recommended settings:

- `CAMERA_MODE=emulated`
- optional `EMULATED_CAMERA_IMAGE_PATH` for deterministic frames

## Option 3: Split Camera and App Deployment

Use this when the camera host must stay close to hardware while the web and AI stack runs elsewhere.

### Camera Host

```powershell
python .\camera_main.py
```

This starts the camera-only service on port `8001`.

### Main App Host

Run the main application with:

- `CAMERA_MODE=remote`
- `REMOTE_CAMERA_BASE_URL=http://<camera-host>:8001`

Then start:

```powershell
python .\main.py
```

## Option 4: Docker for the Main App

`docker-compose.yml` is intended for the main app side, not direct Basler capture.

Recommended pattern:

- Windows host runs `camera_main.py`
- container runs the main app
- main app uses `CAMERA_MODE=remote`
- `REMOTE_CAMERA_BASE_URL=http://host.docker.internal:8001`

Start with:

```powershell
docker compose up --build
```

## Environment Expectations

### Local Camera Mode

- pylon must be installed
- the process must be able to open both cameras
- trigger and pixel format must match the camera setup

### Remote Camera Mode

- the camera host must expose `/status`, `/capture`, and `/camera/alignment`
- network connectivity to `REMOTE_CAMERA_BASE_URL` must be stable
- effective frame freshness depends on remote polling timing

### Emulated Mode

- no camera hardware is required
- this is the safest option for frontend and integration testing

## Verification Checklist

After deployment, verify:

- `GET /status` returns `200`
- `camera.ready` becomes `true` in the chosen mode
- `/capture` returns a JPEG
- the browser page on `/` loads and refreshes
- WebSocket streaming works
- if AI is enabled, `ai.phase` becomes `ready`
- if remote mode is used, the camera service on port `8001` also returns a healthy `/status`

## Operational Notes

- the app is intentionally tolerant of camera startup failures and stays online for diagnostics
- AI startup may take noticeably longer than server startup
- `POST /inference` requires accessible filesystem paths on the machine running the main app
