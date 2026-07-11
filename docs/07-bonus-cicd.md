# 07 — Bonus: automate build + push with GitHub Actions

Steps 02-03 were manual: `docker build`, `docker push`, five times each. `.github/workflows/build-and-push.yml` automates exactly those commands, triggered on every push to `main`.

Read the workflow file side by side with what you typed by hand:

| Manual command | Workflow equivalent |
|---|---|
| `docker login` | `docker/login-action@v3` step, using secrets instead of your typed password |
| `docker build -t $USER/smile-service:v1 models/smile-service` | `docker/build-push-action@v6` with `context: models/smile-service` |
| `docker push $USER/smile-service:v1` | same step, `push: true` |
| repeating for 5 services | `strategy.matrix.service` — one job definition, runs 5 times |

Nothing new conceptually — it's the same 3 commands, run by GitHub's servers instead of your terminal, on a trigger instead of by hand.

## Set it up (optional)

1. Push this repo to GitHub.
2. Create a [Docker Hub access token](https://hub.docker.com/settings/security) (not your password).
3. In the GitHub repo, go to Settings → Secrets and variables → Actions, add:
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN`
4. Push to `main` — check the Actions tab, watch the 5 matrix jobs build and push.

## Why this is a stretch goal, not step 1

Automating a pipeline before you understand its manual steps just hides what's actually happening. You now know what `docker build`/`push` actually do because you ran them by hand first — automating it now is compressing steps you already understand, not skipping steps you don't.

---

That's the full loop: model → serve → containerize → push → deploy → predict. From here, the natural next step (not built out in this repo) is pointing the same manifests at a real AWS EKS cluster instead of `kind` — the YAML barely changes, only the registry auth and cluster target do.
