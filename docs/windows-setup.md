# Windows Setup

Everything in this repo (docs 01-07, DEMO.md) works identically on Windows — same `docker`, `docker-compose`, `kubectl` commands. The only differences are: how you install the tools, and PowerShell syntax instead of bash for a couple of setup one-liners. This doc covers both.

## Required installs

| Tool | Why | Install |
|---|---|---|
| **Git for Windows** | clone the repo | `winget install --id Git.Git -e` |
| **Python 3.11+** | run `python -m venv` for local testing (docs/01) | `winget install --id Python.Python.3.12 -e` |
| **WSL2** | required backend for Docker Desktop on Windows | `wsl --install` (Admin PowerShell), then restart |
| **Docker Desktop** | gives you `docker` CLI + daemon + `docker compose`, all bundled | `winget install --id Docker.DockerDesktop -e` |
| **Docker Hub account** | free, at hub.docker.com — needed to push images (docs/03) | sign up in browser, no install |
| **kubectl** | only needed for docs/04 onward | `winget install --id Kubernetes.kubectl -e` |
| **kind** | only needed for docs/04 onward — or use Docker Desktop's built-in Kubernetes instead (Settings → Kubernetes → Enable) | `winget install --id Kubernetes.kind -e` |

`winget` ships built into Windows 10 (21H2+) and Windows 11. If missing, install "App Installer" from the Microsoft Store first.

## Setup steps

1. **Enable WSL2** (skip if already enabled): open PowerShell **as Administrator**:
   ```powershell
   wsl --install
   ```
   Restart the machine when prompted.

2. **Install Docker Desktop**, launch it from the Start menu, and confirm it's using the WSL2 backend: Settings → General → "Use the WSL 2 based engine" should be checked. Wait for the whale icon to say "Engine running."

3. **Clone the repo**:
   ```powershell
   git clone <repo-url>
   cd ML
   ```

4. **Run the prereq checker**:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\check-prereqs.ps1
   ```
   Add `-Install` to have it install anything missing automatically via winget:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\check-prereqs.ps1 -Install
   ```

5. **Create a Docker Hub account** at hub.docker.com (free), then log in:
   ```powershell
   docker login
   ```

6. **Follow docs/01 onward** — commands are the same as Mac/Linux, with one exception: activating a Python virtual environment.

   | | Mac/Linux | Windows (PowerShell) |
   |---|---|---|
   | Create + activate venv | `python3 -m venv venv && source venv/bin/activate` | `python -m venv venv; venv\Scripts\Activate.ps1` |

   Everything else (`docker build`, `docker-compose up --build`, `kubectl apply`, etc.) is identical on both.

7. **Pushing to Docker Hub**: instead of the bash loop in docs/03, run:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\push-to-dockerhub.ps1 -Username YOUR_DOCKERHUB_USERNAME
   ```
   This builds, tags, and pushes all 5 images, then updates `k8s\*.yaml` to reference them — same result as the manual steps in docs/03, automated. (Mac/Linux equivalent: `./scripts/push-to-dockerhub.sh YOUR_DOCKERHUB_USERNAME`.)

## Windows-specific gotchas

- **"running scripts is disabled on this system"** — PowerShell blocks `.ps1` files by default. Always run with `-ExecutionPolicy Bypass` as shown above, rather than changing your system-wide execution policy.
- **Docker Desktop is a GUI app, not a background service** — unlike colima on Mac, it doesn't auto-start silently. You need to launch it from the Start menu after every reboot and wait for "Engine running" before `docker` commands work.
- **WSL2 install fails / "virtualization not enabled"** — check your BIOS/UEFI for Intel VT-x or AMD-V and enable it; `wsl --install` needs hardware virtualization on.
- **Don't run the `.sh` scripts directly in PowerShell** — `scripts/check-prereqs.sh` and `scripts/push-to-dockerhub.sh` are bash, not PowerShell. Use the `.ps1` versions in this doc, or run the `.sh` versions from WSL2's bash shell if you prefer.
- **Git line-ending warnings on clone** (`LF will be replaced by CRLF`) — harmless for this repo; none of the Dockerfiles or Python code care about line endings.

Once set up, DEMO.md's live-demo flow works exactly the same on Windows — same browser, same webcam permission prompt, same `http://localhost:5000`.
