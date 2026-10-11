#!/usr/bin/env python3
"""Require the exact requested install image to be attested by its manifest."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.artifact_manifest import verify_manifest, ManifestError
from bootstrap_image import parse_bootstrap
from standalone_image import parse_image
from launch_profile import parse_profile


def verify(image):
    image = Path(image).absolute()
    manifest = image.parent / "MANIFEST.json"
    data = verify_manifest(manifest, expected_roles={image.name: "standalone-bootstrap"})
    # Membership is mandatory, even if another valid image sits beside this file.
    record = data["artifacts"][image.name]
    import hashlib
    content = image.read_bytes()
    if len(content) != record["size"] or hashlib.sha256(content).hexdigest() != record["sha256"]:
        raise ManifestError("requested install image differs from recorded artifact")
    outer, inner = parse_bootstrap(content)
    nested, _ = parse_image(inner)
    flags = parse_profile(display=data["display"], debug=data["debug"]).manifest_flags
    if outer.flags != nested.flags or outer.flags != flags:
        raise ManifestError("install image launch flags differ from manifest profile")
    return data


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_install_image.py boot.bin")
    verify(Path(sys.argv[1]))
    print("Requested boot image identity and nested launch profile verified.")
