#!/usr/bin/env python3
"""Checks required tools for this project. One script, runs the same
way on macOS, Linux, and Windows — no separate bash/PowerShell copies
to keep in sync.

Usage:
    python3 scripts/check_prereqs.py
    python3 scripts/check_prereqs.py --install   # auto-install missing tools
"""
import argparse
import platform
import shutil
import subprocess
import sys

OK = "OK"
MISSING = "MISSING"

# Package manager ids per platform. Linux has no single package manager,
# so it only gets a manual link, never an --install attempt.
TOOLS = [
    {"name": "git", "command": "git", "brew": "git", "winget": "Git.Git",
     "manual": "https://git-scm.com/downloads"},
    {"name": "python3", "command": "python3", "brew": None, "winget": "Python.Python.3.12",
     "manual": "https://www.python.org/downloads/"},
    {"name": "docker", "command": "docker", "brew": "--cask docker", "winget": "Docker.DockerDesktop",
     "manual": "https://www.docker.com/products/docker-desktop/"},
    {"name": "kubectl", "command": "kubectl", "brew": "kubectl", "winget": "Kubernetes.kubectl",
     "manual": "https://kubernetes.io/docs/tasks/tools/"},
    {"name": "kind", "command": "kind", "brew": "kind", "winget": "Kubernetes.kind",
     "manual": "https://kind.sigs.k8s.io/docs/user/quick-start/#installation"},
]


def run_ok(cmd: list[str]) -> bool:
    try:
        return subprocess.run(cmd, capture_output=True, timeout=15).returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_tool(tool: dict) -> bool:
    found = shutil.which(tool["command"]) is not None
    # Windows CLIs are sometimes just "python" not "python3".
    if not found and tool["command"] == "python3" and platform.system() == "Windows":
        found = shutil.which("python") is not None
    status = OK if found else MISSING
    print(f"  {status:<8} {tool['name']}")
    return found


def installer_command(system: str) -> str | None:
    """Returns the installer CLI name for this platform, or None if
    there isn't an automated one (e.g. Linux)."""
    if system == "Darwin":
        return "brew"
    if system == "Windows":
        return "winget"
    return None


def install_tool(tool: dict) -> bool:
    """Attempts to install one tool. Returns True only on confirmed
    success — never silently swallows a failed or crashed install."""
    system = platform.system()
    if system == "Darwin" and tool["brew"]:
        cmd = ["brew", "install"] + tool["brew"].split()
    elif system == "Windows" and tool["winget"]:
        cmd = ["winget", "install", "--id", tool["winget"], "-e",
               "--accept-package-agreements", "--accept-source-agreements"]
    else:
        print(f"  No automated installer for {tool['name']} on {system}. Install manually: {tool['manual']}")
        return False

    print(f"Installing {tool['name']} via {cmd[0]}...")
    try:
        result = subprocess.run(cmd)
    except FileNotFoundError:
        print(f"  FAILED: '{cmd[0]}' isn't on PATH, so {tool['name']} wasn't installed. Install manually: {tool['manual']}")
        return False

    if result.returncode != 0:
        print(f"  FAILED: {cmd[0]} exited with code {result.returncode} — see its output above for why. Install manually: {tool['manual']}")
        return False

    print(f"  OK: {tool['name']} installed.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="attempt to install missing tools")
    args = parser.parse_args()

    print("Checking required tools...")
    missing = [tool for tool in TOOLS if not check_tool(tool)]

    print()
    print("Checking Docker daemon...")
    daemon_up = run_ok(["docker", "info"])
    print(f"  {'OK' if daemon_up else 'NOT RUNNING':<8} docker daemon")
    if not daemon_up:
        if platform.system() == "Darwin":
            print("           -> start Docker Desktop, or run 'colima start'")
        else:
            print("           -> start Docker Desktop and wait for 'Engine running'")

    print()
    print("Checking docker compose...")
    compose_ok = run_ok(["docker", "compose", "version"]) or shutil.which("docker-compose") is not None
    print(f"  {'OK' if compose_ok else 'MISSING':<8} docker compose")

    print()
    if not missing and daemon_up and compose_ok:
        print("All set — start at docs/01-train-models.md")
        return 0

    if missing:
        print(f"{len(missing)} tool(s) missing.")
        if args.install:
            installer = installer_command(platform.system())
            if installer and shutil.which(installer) is None:
                store = "the Microsoft Store (search 'App Installer')" if installer == "winget" else "https://brew.sh"
                print(f"'{installer}' isn't on PATH, so nothing can be auto-installed. Install {installer} from {store} first, then re-run with --install.")
                return 1
            results = {tool["name"]: install_tool(tool) for tool in missing}
            succeeded = [name for name, ok in results.items() if ok]
            failed = [name for name, ok in results.items() if not ok]
            print()
            if succeeded:
                print(f"Installed: {', '.join(succeeded)}")
            if failed:
                print(f"Failed: {', '.join(failed)} — see FAILED lines above for why, or install manually.")
            print("Open a new terminal (so PATH refreshes), then re-run this script to confirm.")
        else:
            print("Re-run with --install to install missing tools automatically, or install manually:")
            for tool in missing:
                print(f"  {tool['name']}: {tool['manual']}")

    if not daemon_up or not compose_ok:
        print("Docker daemon / compose issues can't be fixed by --install — see the hints above.")

    return 1 if (missing or not daemon_up or not compose_ok) else 0


if __name__ == "__main__":
    sys.exit(main())
