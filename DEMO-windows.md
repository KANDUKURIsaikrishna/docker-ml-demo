# Live Demo Guide — Windows

Same demo as [DEMO.md](DEMO.md) — identical `docker`/`docker-compose`/`kubectl` commands, since those work the same in PowerShell as bash. Only two things differ: starting Docker, and the checker script invocation. This doc is self-contained so you don't need to flip between files while presenting.

## 0. Before the session

```powershell
python scripts\check_prereqs.py
```

Fix anything marked MISSING. Do this before students arrive, not on stage. First time on this machine? See [docs/windows-setup.md](docs/windows-setup.md).

**Start Docker Desktop** from the Start menu (or pin it to the taskbar for demo day). Wait for the whale icon in the system tray to say "Engine running" — unlike macOS's colima, Docker Desktop is a GUI app, it won't start silently in the background. Do this before you're in front of students; it takes 10-30 seconds.

**Camera + browser check:** this demo needs webcam access over `http://localhost` — browsers allow camera access on `localhost` without HTTPS, but *not* on a plain IP or LAN hostname. If presenting from a laptop projected to a screen, run everything on the presenter's machine and open `http://localhost:5000` there, not from a second machine over the network.

## 1. Start everything

```powershell
docker-compose up --build
```

Wait for `Uvicorn running on http://0.0.0.0:8000` to appear for each service, and the frontend to show its startup line. This builds and starts all 5 containers: frontend, gateway, 3 model services. No training step — the models are pretrained OpenCV cascades baked into the image at `pip install` time.

## 2. Open the app

**http://localhost:5000**

You'll see a dropdown (Smile / Glasses / Eyes), a **Start camera** button, and a **Capture & Predict** button.

## 3. Things to show students, in order

### a. Start the camera
Click **Start camera**, allow browser permission. Live video preview appears. Point out: nothing is sent to the server yet — the video only leaves the browser the moment you click Capture.

### b. Smile detector
Dropdown on "Smile detector." Smile, click **Capture & Predict**.
→ `{"face_detected": true, "smiling": true}`

Now hold a neutral/serious face and capture again.
→ `{"face_detected": true, "smiling": false}`

**Talking point:** this request went browser → frontend → gateway → `smile-service` container, and back, carrying the actual captured JPEG. Same 4-hop pattern as any request in this app — only the payload (an image, not JSON numbers) changed.

### c. Glasses detector
Switch dropdown to "Glasses detector." If you have glasses handy, capture with and without them.
→ with glasses: `{"face_detected": true, "wearing_glasses": true, "edge_density": 0.21}`
→ without: `{"face_detected": true, "wearing_glasses": false, "edge_density": 0.06}`

**Talking point:** open `models/glasses-service/app.py` — there's no "glasses" cascade, because one doesn't exist. It's a heuristic: measure edge density in the strip between your eyes (glasses frames = lots of edges, bare skin = few). Good moment to say plainly: this is not a production-grade classifier, it's tuned to be *demoable*, and the code says so in a comment. Real-world accuracy claims need real evaluation data — worth flagging explicitly so students don't walk away thinking a heuristic like this ships to production as-is.

### d. Eyes open/closed detector
Switch to "Eyes open/closed detector." Capture with eyes open, then try to capture mid-blink or with eyes closed.
→ open: `{"face_detected": true, "eyes_open": true, "eyes_detected": 2}`
→ closed: `{"face_detected": true, "eyes_open": false, "eyes_detected": 0}`

**Talking point:** the trick here is almost sneaky — the eye cascade was *only ever trained on open eyes*, so it simply fails to match closed ones. "No detection" becomes the signal, not an error. Worth a beat: this is inference from an absence, and absences are ambiguous (bad lighting also produces "no detection"). Point at the comment in `app.py` explaining the same limitation.

### e. Break it on purpose (great demo moment)

```powershell
docker stop ml-glasses-service-1
```

Try a Glasses prediction in the UI → gateway returns a clean 503, not a crash:
```json
{"detail": "glasses service unavailable"}
```

**Talking point:** the gateway isolates failure — smile and eyes keep working fine while glasses is down. This is the point of splitting into services instead of one monolith: one model crashing doesn't take down the whole app.

Bring it back:
```powershell
docker start ml-glasses-service-1
```

> Container names come from the folder you cloned into (Docker Compose lowercases it as the project prefix). If you cloned into a folder not named `ML`, run `docker ps` first to get the real names before this step.

### f. Show the Docker side (open a second PowerShell window)

```powershell
docker ps
```
Five containers, five images, five separate processes — point at the `IMAGE` column, each is `ml-<service>`.

```powershell
docker logs ml-gateway-1 --tail 20
```
Shows the routing happening in real time as you click Capture & Predict in the browser.

## 4. If you have time: show it on Kubernetes too

Follow `docs/04-local-k8s-setup.md` onward — commands are identical on Windows (`kubectl`, `kind` behave the same). Same UI, same predictions, but now pods instead of containers, and you can `kubectl delete pod` on a model service mid-demo to show it self-heal (see `docs/06-test-app.md`, section "Confirm it's really Kubernetes"). This is the single best "aha" moment in the whole demo — do it if the session allows.

## 5. Shut down

```powershell
docker-compose down
```

If you also stood up a kind cluster:
```powershell
kind delete cluster --name ml-demo
```
