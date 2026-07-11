# Architecture

Technical reference for how this repo actually works. For the *history* of decisions (why webcam models instead of tabular ones, why kind instead of EKS, etc.) see [docs/superpowers/specs/2026-07-11-ml-docker-deployment-demo-design.md](superpowers/specs/2026-07-11-ml-docker-deployment-demo-design.md) — that doc is the decision log; this doc is the current-state map.

## What this system does

A browser captures a webcam frame, sends it to a model of the user's choosing (smile / glasses / eyes-open detector), and displays the JSON prediction. The prediction itself is intentionally simple (OpenCV Haar cascades, no training) — the actual subject of this repo is everything *around* the prediction: how 5 independent pieces get containerized, wired together, and deployed to Kubernetes.

## System diagram

```
┌─────────────┐      HTTP (page load)       ┌──────────────┐
│   Browser   │ ───────────────────────────▶│   frontend   │
│ (webcam UI) │                              │  Flask :5000 │
└─────────────┘                              └──────┬───────┘
       ▲                                             │
       │ JSON result                    POST image   │ POST image
       │                                (multipart)   ▼
       │                                      ┌──────────────┐
       └──────────────────────────────────────│   gateway    │
                                                │ FastAPI :8000│
                                                └──────┬───────┘
                                                        │ routes by
                                                        │ model name
                                    ┌───────────────────┼───────────────────┐
                                    ▼                   ▼                   ▼
                            ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
                            │ smile-service │   │glasses-service│   │ eyes-service │
                            │ FastAPI :8000 │   │ FastAPI :8000 │   │ FastAPI :8000 │
                            │  OpenCV Haar  │   │  OpenCV Haar  │   │  OpenCV Haar  │
                            └──────────────┘   └──────────────┘   └──────────────┘
```

5 containers, always. Every arrow is a real network hop — nothing is an in-process function call. That's deliberate: it's the same topology whether it's running under Docker Compose (one machine, one network) or Kubernetes (pods, Services, possibly multiple machines).

## Components

| Component | Tech | Responsibility | Key file |
|---|---|---|---|
| `frontend` | Flask, vanilla JS | Serves the webcam-capture page; proxies prediction requests to the gateway server-side (browser never talks to the gateway directly) | `frontend/app.py`, `frontend/static/index.html` |
| `gateway` | FastAPI + httpx | Receives `/predict/{model}`, forwards the image to the right model service by name, returns its response verbatim | `gateway/main.py` |
| `smile-service` | FastAPI + OpenCV | Face cascade → smile cascade on the mouth region | `models/smile-service/app.py` |
| `glasses-service` | FastAPI + OpenCV | Face cascade → eye-line locate → Canny edge density on the nose bridge | `models/glasses-service/app.py` |
| `eyes-service` | FastAPI + OpenCV | Face cascade → eye cascade on the upper face | `models/eyes-service/app.py` |

Each model service is independent: own Dockerfile, own `requirements.txt`, own process. None of them import from each other or share code — deliberate duplication (each one repeats the "decode image → grayscale → face cascade" boilerplate) so that any one of them can be read, understood, and modified in isolation. This is the microservice pattern's actual teaching point: a service's boundary is "what does it do, how do you call it, what does it depend on" — answerable without reading the other four.

## Request lifecycle (one prediction, start to finish)

1. Browser: `getUserMedia()` opens the webcam, `<video>` shows a live preview. Nothing is sent yet.
2. User clicks **Capture & Predict**. JS draws the current video frame to a `<canvas>`, calls `canvas.toBlob()` to get a JPEG, and `POST`s it as `multipart/form-data` to `/api/predict/<model>` on the frontend's own origin (no CORS — browser only ever talks to `localhost:5000`).
3. **frontend** (`frontend/app.py`): reads the uploaded file from `request.files`, re-POSTs the same bytes as multipart to `GATEWAY_URL/predict/<model>`.
4. **gateway** (`gateway/main.py`): looks up `<model>` in a small dict mapping model name → service URL (`SMILE_SERVICE_URL`, etc, read from env vars). Forwards the image to that service's `/predict`. If the model name isn't recognized: `404`. If the service is down or times out: `503` with a clear message — this is what makes the "kill a container mid-demo" moment work.
5. **model service** (e.g. `models/smile-service/app.py`): decodes the JPEG with `cv2.imdecode`, converts to grayscale, runs the face cascade, crops to the relevant sub-region, runs the model-specific cascade or heuristic, returns JSON.
6. Response flows back up the same chain: model service → gateway → frontend → browser, each hop just passing the JSON through unchanged.

Every hop uses the *same* hostname pattern (`smile-service`, `gateway`, etc.) whether running under Docker Compose or Kubernetes — see [Two deployment topologies](#two-deployment-topologies) below for why that's not a coincidence.

## Why 5 separate services, not 1

The alternative (a single FastAPI app with three `if model == ...` branches and three cascades loaded at startup) would be simpler to build and would work fine. It's deliberately not what this repo does, because the entire point is teaching the microservice + orchestration pattern:

- **Independent deployability**: `docker build`/`push`/`deploy` per service means a change to `glasses-service` doesn't require rebuilding or redeploying `smile-service`.
- **Independent failure**: killing `glasses-service` (`docker stop` or `kubectl delete pod`) doesn't take down `smile-service` or `eyes-service` — the gateway just returns a `503` for that one model. A monolith doesn't get to demonstrate this.
- **Independent scaling** (Kubernetes only): `kubectl scale deployment/smile-service --replicas=3` scales just the popular model, not the whole app.

## Docker strategy

Every service's `Dockerfile` follows the identical shape:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

`requirements.txt` is copied and installed *before* the application code. Docker caches each instruction as a layer; reordering those two lines would mean every code edit invalidates the (large, slow) dependency-install layer instead of just the (small, fast) code-copy layer. This matters more here than in a typical app because `opencv-python-headless` is a meaningfully large dependency.

No multi-stage builds — dependencies are small enough (FastAPI, uvicorn, OpenCV, httpx/requests) that the lesson stays on layer caching rather than multi-stage complexity. No base-image variation across services — using the same `python:3.11-slim` everywhere means a layer pulled for one image is already cached for the next.

The model services ship **zero trained artifacts** — no `.pkl`, no dataset. `cv2.data.haarcascades` points at XML classifier files bundled *inside* the `opencv-python-headless` package itself, so `pip install` is the entire "model delivery" step. See [docs/01-train-models.md](01-train-models.md) for the reasoning.

## Two deployment topologies

The same 5 images run under two completely independent orchestration mechanisms — `docker-compose.yml` and `k8s/*.yaml` never reference each other:

| | Docker Compose | Kubernetes (kind) |
|---|---|---|
| Defined in | `docker-compose.yml` | `k8s/*.yaml` (5 `Deployment`+`Service` pairs + a `Namespace`) |
| Networking | Compose's private per-project network; service name = DNS name | Kubernetes `Service` objects; service name = DNS name |
| Failure recovery | None — a stopped container stays stopped | `Deployment` controller restarts crashed/deleted pods automatically |
| Scaling | `docker-compose up --scale smile-service=3` (manual, ad hoc) | `kubectl scale deployment/smile-service --replicas=3` (declarative) |
| Used for | Fast local iteration (docs 01-03), the Compose half of the live demo | The actual orchestration lesson (docs 04-06 / `docs/kind-deployment.md`) |

The reason `gateway`'s code never has to change between the two: both mechanisms resolve a plain hostname like `smile-service` to the right container/pod via their own internal DNS. The gateway just calls `http://smile-service:8000` and trusts whatever's underneath to route it correctly — that's the actual abstraction Kubernetes Services (and Compose networks) provide.

### Kubernetes object shape

Each of the 5 `k8s/*-deployment.yaml` files defines one `Deployment` (keeps N replicas of a pod running, restarts on failure) and one `Service` (stable DNS name + address for those pods) in a single file. All 5 live in the `ml-demo` namespace. Model services and the gateway are `ClusterIP` (internal-only); `frontend` is `NodePort` so it's reachable from outside the cluster — in practice we still use `kubectl port-forward` rather than the NodePort directly, since that's simpler for a local kind cluster (see `docs/kind-deployment.md`).

No Ingress, no TLS, no autoscaling, no resource limits/requests — all explicitly out of scope (see the design spec's "Out of scope" section). No `kustomize` — see the note below.

## Why not kustomize

Kustomize earns its cost when you have *multiple variants* of the same manifests (dev/staging/prod, differing replica counts or resource limits per environment) that would otherwise mean duplicated YAML — its overlay mechanism lets you patch a shared base instead of copy-pasting. This repo has exactly one environment (local kind, one replica per service), so there's nothing to de-duplicate. Introducing `kustomization.yaml` + bases/overlays here would add a concept for students to learn that doesn't pay for itself yet.

The one place kustomize would be a genuinely cleaner fit: image-name substitution. `scripts/push_to_dockerhub.py` currently rewrites `k8s/*.yaml` with a regex to swap in your Docker Hub username — that's a manual version of kustomize's built-in `images:` transformer. Worth adopting if this repo ever grows a real multi-environment split (e.g. the deferred EKS path).

## Model layer: why heuristics, not trained models

All three "models" are OpenCV Haar cascades — pretrained pattern classifiers that ship inside `opencv-python-headless`, not anything trained in this repo. `glasses-service` additionally uses a hand-written heuristic (Canny edge density on the nose bridge) since no cascade classifies "wearing glasses" directly. This was a deliberate pivot (see the design spec's 2026-07-11 addendum) from an earlier version using real scikit-learn models (iris/diabetes/spam) — those were more "correct" ML but produced numeric feature vectors nobody could evaluate by eye during a live demo. The tradeoff: these heuristics are demonstrably not production-accurate (see the false-negative bugs found and fixed post-launch — smile cascade scoped to the wrong region, glasses cascade failing specifically on glasses-wearers, eyes requiring both eyes detected). That's disclosed explicitly in code comments and `docs/01-train-models.md` rather than hidden.

## Repo map

```
frontend/            Flask app, webcam UI, proxies to gateway
gateway/              FastAPI, routes /predict/{model} to the right service
models/
  smile-service/       independent FastAPI + OpenCV service
  glasses-service/      independent FastAPI + OpenCV service
  eyes-service/           independent FastAPI + OpenCV service
k8s/                  Deployment + Service manifests, one pair per component
docker-compose.yml     all 5 services, local network, fast iteration
scripts/
  check_prereqs.py       cross-platform tool/daemon check, optional --install
  push_to_dockerhub.py    build+tag+push all 5 images, rewrite k8s manifests
docs/                 numbered tutorial (01-07), plus reference docs:
  ARCHITECTURE.md         this file
  kind-deployment.md       full kind walkthrough in one file
  windows-setup.md          Windows-specific install/gotchas
  superpowers/specs/         design history
.github/workflows/     bonus CI/CD, mirrors docs/03's manual steps
DEMO.md / DEMO-windows.md          Compose live-demo scripts
DEMO-kind.md / DEMO-kind-windows.md   Kubernetes live-demo scripts
```

## Extension points

Things explicitly deferred, in rough order of how much they'd change this architecture:

- **Real AWS EKS deployment** — `k8s/*.yaml` has zero cloud-specific fields, so the manifests themselves need no changes; only image registry auth and cluster target would differ from the kind path.
- **Ingress / TLS** — would replace the `port-forward`/`NodePort` access pattern with a real routable URL; not needed for a local single-user demo.
- **Autoscaling / resource limits** — meaningful once there's real traffic to scale against; a teaching demo has none.
- **kustomize** — see above; adopt if a second environment ever appears.
- **CI/CD beyond the build/push bonus** — `.github/workflows/build-and-push.yml` only automates the manual steps in docs/03; it doesn't run tests, lint, or gate deploys.
