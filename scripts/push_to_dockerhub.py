#!/usr/bin/env python3
"""Builds and pushes all 5 images to Docker Hub, then rewrites the k8s
manifests to reference them. Automates the manual loop in
docs/03-push-dockerhub.md — read that doc first if you want to
understand each step before running this. One script, runs the same
way on macOS, Linux, and Windows.

Usage:
    python3 scripts/push_to_dockerhub.py YOUR_DOCKERHUB_USERNAME
    python3 scripts/push_to_dockerhub.py YOUR_DOCKERHUB_USERNAME --tag v2
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SERVICES = ["smile-service", "glasses-service", "eyes-service", "gateway", "frontend"]
PLACEHOLDER = "REPLACE_WITH_YOUR_DOCKERHUB_USERNAME"


def run(cmd: list[str]) -> None:
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=REPO_ROOT)
    if result.returncode != 0:
        sys.exit(f"Command failed: {' '.join(cmd)}")


def build_context(service: str) -> Path:
    models_path = REPO_ROOT / "models" / service
    return models_path if models_path.is_dir() else REPO_ROOT / service


def update_k8s_manifests(username: str, tag: str) -> None:
    pattern = re.compile(rf"{PLACEHOLDER}/([a-z-]+):v1")
    for manifest in (REPO_ROOT / "k8s").glob("*.yaml"):
        text = manifest.read_text()
        new_text = pattern.sub(rf"{username}/\1:{tag}", text)
        if new_text != text:
            manifest.write_text(new_text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="your Docker Hub username")
    parser.add_argument("--tag", default="v1", help="image tag (default: v1)")
    args = parser.parse_args()

    print("Logging in to Docker Hub...")
    run(["docker", "login"])

    for service in SERVICES:
        image = f"{args.username}/{service}:{args.tag}"
        print(f"\nBuilding and pushing {image} ...")
        run(["docker", "build", "-t", image, str(build_context(service))])
        run(["docker", "push", image])

    print(f"\nUpdating k8s manifests to reference {args.username}/*:{args.tag} ...")
    update_k8s_manifests(args.username, args.tag)

    print("\nDone. Pushed images:")
    for service in SERVICES:
        print(f"  {args.username}/{service}:{args.tag}")
    print("\nk8s/*.yaml now point at your images. Continue at docs/04-local-k8s-setup.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
