# Live Demo Guide

For running the app live in front of students — fastest path to a working UI, minimal talking-while-typing.

## 0. Before the session

```bash
./scripts/check-prereqs.sh
```

Fix anything marked MISSING. Do this before students arrive, not on stage.

If Docker isn't running yet:

```bash
# Docker Desktop: open the app, wait for the whale icon to go steady
# colima (no Docker Desktop installed): 
colima start
```

## 1. Train the models (one-time, or if you deleted the .pkl files)

```bash
for svc in iris-service diabetes-service spam-service; do
  cd models/$svc
  python3 -m venv venv && source venv/bin/activate
  pip install -q -r requirements.txt
  python train.py
  deactivate
  cd ../..
done
```

Skip this if `models/*/model.pkl` already exist — they're checked into the repo.

## 2. Start everything

```bash
docker-compose up --build
```

Wait for `Uvicorn running on http://0.0.0.0:8000` to appear for each service, and the frontend to show its startup line. This builds and starts all 5 containers: frontend, gateway, 3 model services.

## 3. Open the app

**http://localhost:5000**

You'll see a dropdown (Iris / Diabetes / Spam) and an input area that changes based on your selection, plus a Predict button.

## 4. Things to show students, in order

### a. Iris classifier — the simple case
Leave the defaults (5.1, 3.5, 1.4, 0.2), hit Predict.
→ `{"prediction": "setosa", "confidence": 1.0}`

Change petal length/width to something like `6.0, 2.5` → try `virginica`-leaning values (e.g. sepal 6.7, 3.1, petal 4.7, 1.5) to get a different class:
→ `{"prediction": "versicolor", "confidence": ...}`

**Talking point:** this request went browser → frontend → gateway → `iris-service` container, and back. Four hops, one dropdown click.

### b. Diabetes — regression, not classification
Switch dropdown to Diabetes, leave default 10 comma-separated values, Predict.
→ `{"prediction": 244.0}` (a number, not a class label)

**Talking point:** same pattern (own container, own Dockerfile, own model.pkl) but the output shape is completely different — this is why each model gets its own service instead of one giant if/else in a single container.

### c. Spam — two artifacts, not one
Switch to Spam, try:
- `"WINNER!! Claim your free prize now!"` → `{"prediction": "spam", ...}`
- `"Hey are we still on for lunch tomorrow?"` → `{"prediction": "ham", ...}`

**Talking point:** open `models/spam-service/app.py` and point out it loads *two* files at startup (`model.pkl` and `vectorizer.pkl`) — not every model ships as a single artifact, and the container doesn't care, it just loads whatever the service needs.

### d. Break it on purpose (great demo moment)

```bash
docker stop ml-spam-service-1
```

Try a Spam prediction in the UI → gateway returns a clean 503, not a crash:
```json
{"detail": "spam service unavailable"}
```

**Talking point:** the gateway isolates failure — iris and diabetes keep working fine while spam is down. This is the point of splitting into services instead of one monolith: one model crashing doesn't take down the whole app.

Bring it back:
```bash
docker start ml-spam-service-1
```

### e. Show the Docker side (open a second terminal)

```bash
docker ps
```
Five containers, five images, five separate processes — point at the `IMAGE` column, each is `ml-<service>`.

```bash
docker logs ml-gateway-1 --tail 20
```
Shows the routing happening in real time as you click Predict in the browser.

## 5. If you have time: show it on Kubernetes too

Follow `docs/04-local-k8s-setup.md` onward — same UI, same predictions, but now pods instead of containers, and you can `kubectl delete pod` on a model service mid-demo to show it self-heal (see `docs/06-test-app.md`, section "Confirm it's really Kubernetes"). This is the single best "aha" moment in the whole demo — do it if the session allows.

## 6. Shut down

```bash
docker-compose down
```

If you also stood up a kind cluster:
```bash
kind delete cluster --name ml-demo
```
