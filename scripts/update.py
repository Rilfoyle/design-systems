#!/usr/bin/env python3
"""Refresh selected, unmodified official snapshots from their configured sources."""
from __future__ import annotations

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "sources.json"
LOCK = ROOT / "sources.lock.json"


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            digest.update(f"L\0{relative}\0{os.readlink(path)}\0".encode())
        elif path.is_file():
            digest.update(f"F\0{relative}\0{digest_file(path)}\0".encode())
    return digest.hexdigest()


def run(command: list[str]) -> str:
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(f"Command failed: {' '.join(command)}\n{result.stderr.strip()}")
    return result.stdout.strip()


def safe_extract(archive: Path, target: Path) -> None:
    """Reject paths and links that could escape the destination."""
    with tarfile.open(archive, "r:*") as contents:
        for member in contents.getmembers():
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                raise RuntimeError(f"Unexpected archive member: {member.name}")
            if not (member.isfile() or member.isdir()):
                raise RuntimeError(f"Unsupported archive member: {member.name}")
        if hasattr(tarfile, "data_filter"):
            contents.extractall(target, filter="data")
        else:
            contents.extractall(target)


def build_snapshot(system: str, config: dict, scratch: Path) -> tuple[Path, dict]:
    stage = scratch / "stage" / system / "official"
    stage.mkdir(parents=True)
    result = {"git": {}}
    for source in config.get("git", []):
        source_id = source["id"]
        print(f"  {source_id}: {source['url']} ({source['branch']})", flush=True)
        clone = scratch / "clones" / system / source_id
        clone.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--quiet", "--depth=1", "--filter=blob:none", "--no-checkout",
             "--single-branch", "--branch", source["branch"], source["url"], str(clone)])
        commit = run(["git", "-C", str(clone), "rev-parse", "HEAD"])
        archive = scratch / f"{system}-{source_id}.tar"
        run(["git", "-C", str(clone), "archive", "--format=tar", f"--output={archive}",
             "HEAD", "--", *source["paths"]])
        destination = stage / source_id
        destination.mkdir(parents=True)
        safe_extract(archive, destination)
        result["git"][source_id] = {"url": source["url"], "branch": source["branch"], "commit": commit}
    for source in config.get("npm", []):
        source_id = source["id"]
        registry = "https://registry.npmjs.org/"
        metadata_url = registry + urllib.parse.quote(source["name"], safe="") + "/" + urllib.parse.quote(source["tag"], safe="")
        print(f"  npm/{source_id}: {source['name']} ({source['tag']})", flush=True)
        request = urllib.request.Request(metadata_url, headers={"User-Agent": "design-systems-snapshot/1.0"})
        with urllib.request.urlopen(request, timeout=45) as response:
            metadata = json.load(response)
        if metadata.get("name") != source["name"]:
            raise RuntimeError(f"Unexpected npm package metadata: {metadata_url}")
        distribution = metadata["dist"]
        tarball = distribution["tarball"]
        url = urllib.parse.urlparse(tarball)
        if url.scheme != "https" or url.hostname != "registry.npmjs.org":
            raise RuntimeError(f"Unexpected npm tarball URL: {tarball}")
        integrity = distribution.get("integrity", "")
        if not integrity.startswith("sha512-"):
            raise RuntimeError(f"Missing SHA-512 integrity: {source['name']}")
        request = urllib.request.Request(tarball, headers={"User-Agent": "design-systems-snapshot/1.0"})
        with urllib.request.urlopen(request, timeout=45) as response:
            data = response.read(60 * 1024 * 1024 + 1)
        if len(data) > 60 * 1024 * 1024:
            raise RuntimeError(f"Unexpected npm tarball size: {source['name']}")
        actual = "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode("ascii")
        if not hmac.compare_digest(integrity, actual):
            raise RuntimeError(f"Integrity mismatch: {source['name']}")
        archive = scratch / f"{system}-npm-{source_id}.tgz"
        archive.write_bytes(data)
        extraction = scratch / "npm" / system / source_id
        extraction.mkdir(parents=True)
        safe_extract(archive, extraction)
        package = extraction / "package"
        package_metadata = json.loads((package / "package.json").read_text(encoding="utf-8"))
        if package_metadata.get("name") != source["name"] or package_metadata.get("version") != metadata["version"]:
            raise RuntimeError(f"Unexpected contents in npm tarball: {source['name']}")
        if not (package / "LICENSE").is_file():
            raise RuntimeError(f"Missing npm package license: {source['name']}")
        destination = stage / "npm" / source_id
        destination.parent.mkdir(parents=True, exist_ok=True)
        package.replace(destination)
        result.setdefault("npm", {})[source_id] = {
            "name": source["name"], "tag": source["tag"], "version": metadata["version"],
            "tarball": tarball, "integrity": integrity,
        }
    result["tree_sha256"] = tree_digest(stage)
    return stage, result


def check_clean(system: str, locked: dict | None) -> None:
    destination = ROOT / system / "official"
    if not destination.exists():
        if locked:
            raise RuntimeError(f"{destination} is missing. Restore it before updating.")
        return
    if not locked:
        raise RuntimeError(f"{destination} exists without a lock entry; refusing to replace it.")
    if tree_digest(destination) != locked.get("tree_sha256"):
        raise RuntimeError(f"{destination} contains local changes; restore or move them before updating.")


def main() -> int:
    config = json.loads(MANIFEST.read_text(encoding="utf-8"))["systems"]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system", action="append", choices=sorted(config), help="Update one system; repeat to select several.")
    parser.add_argument("--check", action="store_true", help="Fetch and compare without changing files. Exit 2 if updates exist.")
    args = parser.parse_args()
    selected = list(dict.fromkeys(args.system or config.keys()))
    old_lock_bytes = LOCK.read_bytes() if LOCK.exists() else None
    lock = json.loads(old_lock_bytes) if old_lock_bytes else {"version": 1, "systems": {}}
    locked_systems = lock.setdefault("systems", {})
    for system in selected:
        check_clean(system, locked_systems.get(system))
    with tempfile.TemporaryDirectory(prefix=".design-systems-update-", dir=ROOT) as temp_dir:
        scratch = Path(temp_dir)
        stages = {}
        updated = {}
        with ThreadPoolExecutor(max_workers=min(4, len(selected))) as executor:
            pending = {}
            for system in selected:
                print(f"Checking {system}...", flush=True)
                pending[system] = executor.submit(build_snapshot, system, config[system], scratch)
            for system in selected:
                stages[system], updated[system] = pending[system].result()
        changed = [system for system in selected if updated[system] != locked_systems.get(system)]
        if not changed:
            print("All selected snapshots are up to date.")
            return 0
        print("Updates available: " + ", ".join(changed))
        if args.check:
            return 2
        # Recheck after fetching so other changes are never silently overwritten.
        if (LOCK.read_bytes() if LOCK.exists() else None) != old_lock_bytes:
            raise RuntimeError("The lock file changed while fetching; please rerun the update.")
        for system in changed:
            check_clean(system, locked_systems.get(system))
        backups = {}
        applied = []
        try:
            for system in changed:
                destination = ROOT / system / "official"
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists():
                    backup = scratch / "backups" / system
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    destination.replace(backup)
                    backups[system] = backup
                stages[system].replace(destination)
                applied.append(system)
            for system in changed:
                locked_systems[system] = updated[system]
            new_lock = scratch / "sources.lock.json"
            new_lock.write_text(json.dumps(lock, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            new_lock.replace(LOCK)
        except Exception:
            for system in reversed(changed):
                destination = ROOT / system / "official"
                if system in applied and destination.exists():
                    shutil.rmtree(destination)
                if system in backups:
                    backups[system].replace(destination)
            raise
    print("Updated official snapshots and sources.lock.json. Review the Git diff before committing.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError, KeyError, tarfile.TarError, subprocess.SubprocessError) as error:
        print(f"Update failed: {error}", file=sys.stderr)
        sys.exit(1)
