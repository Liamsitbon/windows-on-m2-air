#!/usr/bin/env python3
"""Stage the J413 firmware overlay without replacing upstream tracked files."""

import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from guest_layout import load_layout, render_dsc, validate_fdf

MU_REVISION = "8b4dc4b4e3ff8606d0af36163acf9de79b7b4737"
OVERLAY = ROOT / "platforms/j413/mu"
PLATFORM = OVERLAY / "Platform/MacBookAirM2Pkg"


def check_overlay(root=ROOT):
    layout = load_layout(root / "config/j413-guest-layout.json")
    platform = root / "platforms/j413/mu/Platform/MacBookAirM2Pkg"
    validate_fdf(layout, (platform / "MacBookAirM2.fdf").read_text())
    if (platform / "J413GuestLayout.dsc.inc").read_text() != render_dsc(layout):
        raise ValueError("J413 generated DSC include is stale")
    return layout


def stage_overlay(root=ROOT):
    check_overlay(root)
    mu = root / "mu"
    revision = subprocess.check_output(
        ["git", "-C", str(mu), "rev-parse", "HEAD"], text=True
    ).strip()
    if revision != MU_REVISION:
        raise ValueError(f"J413 overlay requires pinned Mu {MU_REVISION}, got {revision}")
    sources = sorted((root / "platforms/j413/mu").rglob("*"))
    copies = []
    # Preflight every destination before changing anything. Never overwrite a
    # developer's edits or a tracked upstream source file.
    for source in sources:
        if not source.is_file():
            continue
        relative = source.relative_to(root / "platforms/j413/mu")
        target = mu / relative
        tracked = subprocess.check_output(
            ["git", "-C", str(mu), "ls-files", "--", relative.as_posix()]
        )
        if tracked:
            raise ValueError(f"overlay would overwrite upstream source: {relative}")
        if target.exists() and target.read_bytes() != source.read_bytes():
            raise ValueError(f"overlay destination has local edits: {relative}")
        copies.append((source, target))
    for source, target in copies:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return copies


def overlay_sha256(root=ROOT):
    digest = hashlib.sha256()
    directory = root / "platforms/j413/mu"
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(directory).as_posix().encode() + b"\0")
            digest.update(path.read_bytes())
    return digest.hexdigest()


def stage_m1n1(root=ROOT):
    source = root / "m1n1_windows"
    revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if revision != "9cd80ac652ac404e92ae279deeaec8c629d7d184":
        raise ValueError("J413 m1n1 patches require the pinned main baseline")
    pending = []
    for patch in sorted((root / "platforms/j413/patches").glob("*.patch")):
        command = ["git", "-C", str(source), "apply", "--check"]
        applied = subprocess.run(command + ["--reverse", str(patch.resolve())], capture_output=True)
        if applied.returncode == 0:
            continue
        result = subprocess.run(command + [str(patch.resolve())], capture_output=True, text=True)
        if result.returncode:
            raise ValueError(f"patch conflicts with local source: {patch.name}: {result.stderr}")
        pending.append(patch)
    for patch in pending:
        subprocess.run(["git", "-C", str(source), "apply", str(patch.resolve())], check=True)
    return pending


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", action="store_true")
    parser.add_argument("--stage-m1n1", action="store_true")
    args = parser.parse_args()
    try:
        layout = check_overlay()
        if args.stage:
            stage_overlay()
        if args.stage_m1n1:
            stage_m1n1()
        print(f"J413 firmware contract: {layout.cpu_count} CPUs; "
              f"{layout.virtual_fb_width}x{layout.virtual_fb_height}; "
              f"overlay sha256={overlay_sha256()}")
        print("Experimental firmware only; M2 Windows boot and GPU are unqualified.")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
