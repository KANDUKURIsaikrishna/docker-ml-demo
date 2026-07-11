# Windows Setup

Everything in this repo (docs 01-07, DEMO.md) works identically on Windows — same `docker`, `docker-compose`, `kubectl` commands, and the same `scripts/check_prereqs.py` / `scripts/push_to_dockerhub.py` (Python, not bash or PowerShell, so no separate Windows-only script to maintain). The only real differences are: how you install the tools, and one PowerShell line for activating a Python virtual environment. This doc covers both.

## Required installs

| Tool | Why | Install |
|---|---|---|
| **Git for Windows** | clone the repo | `winget install --id Git.Git -e` |
| **Python 3.11+** | run the checker script + `python -m venv` for local testing (docs/01) | `winget install --id Python.Python.3.12 -e` |
| **WSL2** | required backend for Docker Desktop on Windows | `wsl --install` (Admin PowerShell), then restart |
| **Docker Desktop** | gives you `docker` CLI + daemon + `docker compose`, all bundled | `winget install --id Docker.DockerDesktop -e` |
| **Docker Hub account** | free, at hub.docker.com — needed to push images (docs/03) | sign up in browser, no install |
| **kubectl** | only needed for docs/04 onward | `winget install --id Kubernetes.kubectl -e` |
| **kind** | only needed for docs/04 onward — or use Docker Desktop's built-in Kubernetes instead (Settings → Kubernetes → Enable) | `winget install --id Kubernetes.kind -e` |

`winget` ships built into Windows 10 (21H2+) and Windows 11. If missing, install "App Installer" from the Microsoft Store first.

Python is the one tool you have to install by hand before anything else — the checker script needs Python to run, so it can't check for its own absence.

## Setup steps

1. **Enable WSL2** (skip if already enabled): open PowerShell **as Administrator**:
   ```powershell
   wsl --install
   ```
   Restart the machine when prompted.

2. **Install Python**, if you don't already have it: `winget install --id Python.Python.3.12 -e`.

3. **Install Docker Desktop**, launch it from the Start menu, and confirm it's using the WSL2 backend: Settings → General → "Use the WSL 2 based engine" should be checked. Wait for the whale icon to say "Engine running."

4. **Clone the repo**:
   ```powershell
   git clone <repo-url>
   cd ML
   ```

5. **Run the prereq checker** — same script as macOS/Linux:
   ```powershell
   python scripts\check_prereqs.py
   ```
   Add `--install` to have it install anything else missing automatically via winget:
   ```powershell
   python scripts\check_prereqs.py --install
   ```

6. **Create a Docker Hub account** at hub.docker.com (free), then log in:
   ```powershell
   docker login
   ```

7. **Follow docs/01 onward** — commands are the same as Mac/Linux, with one exception: activating a Python virtual environment.

   | | Mac/Linux | Windows (PowerShell) |
   |---|---|---|
   | Create + activate venv | `python3 -m venv venv && source venv/bin/activate` | `python -m venv venv; venv\Scripts\Activate.ps1` |

   Everything else (`docker build`, `docker-compose up --build`, `kubectl apply`, etc.) is identical on both.

8. **Pushing to Docker Hub** — same script as macOS/Linux:
   ```powershell
   python scripts\push_to_dockerhub.py YOUR_DOCKERHUB_USERNAME
   ```
   This builds, tags, and pushes all 5 images, then updates `k8s\*.yaml` to reference them — same result as the manual steps in docs/03, automated.

## Windows-specific gotchas

- **Docker Desktop is a GUI app, not a background service** — unlike colima on Mac, it doesn't auto-start silently. You need to launch it from the Start menu after every reboot and wait for "Engine running" before `docker` commands work.
- **WSL2 install fails / "virtualization not enabled"** — check your BIOS/UEFI for Intel VT-x or AMD-V and enable it; `wsl --install` needs hardware virtualization on.
- **`python` vs `python3`** — Windows installs usually only register `python`, not `python3`. `scripts/check_prereqs.py` accounts for this automatically; if you're typing commands from docs/01 by hand, use `python` instead of `python3` on Windows.
- **Git line-ending warnings on clone** (`LF will be replaced by CRLF`) — harmless for this repo; none of the Dockerfiles or Python code care about line endings.

Once set up, DEMO.md's live-demo flow works exactly the same on Windows — same browser, same webcam permission prompt, same `http://localhost:5000`.
