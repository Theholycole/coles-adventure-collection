#!/usr/bin/env python3
"""Publish a built module folder as a GitHub release that Forge and Foundry can install.

Usage:
    python3 release.py "<path>/v1.4.2/lantern-house"            # build, commit, push, release
    python3 release.py "<path>/v1.4.2/lantern-house" --dry-run  # build .build/ only

The folder is the module itself (module.json at its top). It is never modified:
the script writes a copy of module.json with the url/manifest/download fields,
fixes that line in SHA256SUMS.txt, and zips everything with module.json at the
ZIP root. The release gets two assets, module.json and module.zip, so the
manifest URL below always points at the newest version.
"""

import hashlib
import json
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

REPO = "Theholycole/coles-adventure-collection"
PAGE = f"https://github.com/{REPO}"
MANIFEST = f"{PAGE}/releases/latest/download/module.json"
HERE = Path(__file__).resolve().parent
BUILD = HERE / ".build"
JUNK = {".DS_Store", "Thumbs.db", "desktop.ini"}
STORED = {".png", ".jpg", ".jpeg", ".webp", ".webm", ".mp4", ".mp3", ".ogg", ".m4a", ".zip"}


def run(*cmd, check=True):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, cwd=HERE, check=check)


def released_manifest(src_manifest, tag):
    """module.json with the GitHub fields placed right after "version"."""
    out = {}
    for key, value in src_manifest.items():
        if key in ("url", "manifest", "download"):
            continue
        out[key] = value
        if key == "version":
            out["url"] = PAGE
            out["manifest"] = MANIFEST
            out["download"] = f"{PAGE}/releases/download/{tag}/module.zip"
    return (json.dumps(out, indent=2, ensure_ascii=False) + "\n").encode()


def fixed_sums(sums_text, manifest_bytes):
    digest = hashlib.sha256(manifest_bytes).hexdigest()
    lines = []
    for line in sums_text.splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2 and parts[1].strip() == "module.json":
            line = f"{digest}  module.json"
        lines.append(line)
    return ("\n".join(lines) + "\n").encode()


def top_release_notes(src):
    """The first "# ..." section of RELEASE-NOTES.md, without its heading."""
    path = src / "RELEASE-NOTES.md"
    if not path.exists():
        return ""
    section, started = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            if started:
                break
            started = True
            continue
        if started:
            section.append(line)
    return "\n".join(section).strip()


def build_zip(src, replacements, dest):
    files = sorted(p for p in src.rglob("*") if p.is_file() and p.name not in JUNK)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in files:
            name = path.relative_to(src).as_posix()
            kind = zipfile.ZIP_STORED if path.suffix.lower() in STORED else zipfile.ZIP_DEFLATED
            if name in replacements:
                zf.writestr(zipfile.ZipInfo.from_file(path, name), replacements[name], compress_type=kind)
            else:
                zf.write(path, name, compress_type=kind)
    return len(files)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if len(args) != 1:
        sys.exit(__doc__)
    src = Path(args[0]).expanduser().resolve()
    if not (src / "module.json").is_file():
        sys.exit(f"No module.json in {src}")

    src_manifest = json.loads((src / "module.json").read_text(encoding="utf-8"))
    version = src_manifest["version"]
    tag = f"v{version}"
    if not dry:
        exists = subprocess.run(["gh", "release", "view", tag, "--repo", REPO],
                                cwd=HERE, capture_output=True).returncode == 0
        if exists:
            sys.exit(f"{tag} is already released. Bump \"version\" in {src / 'module.json'} first.")

    manifest_bytes = released_manifest(src_manifest, tag)
    replacements = {"module.json": manifest_bytes}
    if (src / "SHA256SUMS.txt").exists():
        replacements["SHA256SUMS.txt"] = fixed_sums(
            (src / "SHA256SUMS.txt").read_text(encoding="utf-8"), manifest_bytes)

    BUILD.mkdir(exist_ok=True)
    (BUILD / "module.json").write_bytes(manifest_bytes)
    count = build_zip(src, replacements, BUILD / "module.zip")
    notes = top_release_notes(src) or f"Version {version}."
    (BUILD / "notes.md").write_text(notes + "\n", encoding="utf-8")
    size = (BUILD / "module.zip").stat().st_size / 1e6
    print(f"Built {tag}: {count} files, module.zip {size:.0f} MB")
    if dry:
        print(f"Dry run: see {BUILD}")
        return

    (HERE / "module.json").write_bytes(manifest_bytes)
    run("git", "add", "module.json")
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=HERE).returncode != 0:
        run("git", "commit", "-m", f"Release {tag}")
    run("git", "push", "origin", "main")
    run("gh", "release", "create", tag, "--repo", REPO, "--target", "main",
        "--title", f"{src_manifest.get('title', 'Release')} {version}",
        "--notes-file", str(BUILD / "notes.md"),
        str(BUILD / "module.json"), str(BUILD / "module.zip"))

    with urllib.request.urlopen(MANIFEST) as response:
        live = json.load(response)
    if live.get("version") != version:
        sys.exit(f"Released, but the manifest URL still reports {live.get('version')}.")
    print(f"Done: {MANIFEST} now reports {version}.")


if __name__ == "__main__":
    main()
