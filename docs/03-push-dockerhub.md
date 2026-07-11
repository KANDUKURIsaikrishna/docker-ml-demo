# 03 — Push images to Docker Hub

Kubernetes doesn't build images — it only pulls already-built images from a registry. Docker Hub is that registry here.

## 1. Create a Docker Hub account (if you don't have one)

https://hub.docker.com — free tier is enough for this demo.

## 2. Log in from the CLI

```bash
docker login
```

## 3. Tag and push each image

Image names on Docker Hub must be `<your-username>/<image-name>:<tag>`. Replace `YOUR_USERNAME` below with your actual Docker Hub username.

```bash
export DOCKERHUB_USERNAME=YOUR_USERNAME

for svc in smile-service glasses-service eyes-service; do
  docker build -t $DOCKERHUB_USERNAME/$svc:v1 models/$svc
  docker push $DOCKERHUB_USERNAME/$svc:v1
done

docker build -t $DOCKERHUB_USERNAME/gateway:v1 gateway
docker push $DOCKERHUB_USERNAME/gateway:v1

docker build -t $DOCKERHUB_USERNAME/frontend:v1 frontend
docker push $DOCKERHUB_USERNAME/frontend:v1
```

Check https://hub.docker.com/repositories/YOUR_USERNAME — you should see all 5 repositories.

**Why this step matters:** everything up to now only existed on your laptop. `docker push` is the moment your image becomes something *any machine* (a teammate's laptop, a CI runner, a Kubernetes node) can pull and run without having your source code or having run `docker build` themselves. This is the same reason `git push` matters for code — an image sitting only in your local Docker cache isn't deployable by anyone else.

## 4. Point the K8s manifests at your images

Each file in `k8s/*-deployment.yaml` has a placeholder:

```yaml
image: REPLACE_WITH_YOUR_DOCKERHUB_USERNAME/smile-service:v1
```

Replace `REPLACE_WITH_YOUR_DOCKERHUB_USERNAME` with your actual username in all 5 manifest files before moving on — a quick way:

```bash
sed -i '' "s/REPLACE_WITH_YOUR_DOCKERHUB_USERNAME/$DOCKERHUB_USERNAME/g" k8s/*.yaml
```

(Drop the `''` after `-i` if you're on Linux, not macOS.)

## Doing this again later

Once you understand what the commands above actually do, `scripts/push_to_dockerhub.py` automates steps 2-4 in one command — same script on macOS, Linux, and Windows:

```bash
python3 scripts/push_to_dockerhub.py YOUR_DOCKERHUB_USERNAME
```

Same reasoning as the CI/CD bonus in docs/07: automate it after you've done it by hand once, not instead of.

Next: [04 — Local Kubernetes setup](04-local-k8s-setup.md)
