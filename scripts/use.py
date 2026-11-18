#!/usr/bin/env python3
"""Copy an official skill, optionally with official DESIGN.md files, into a project."""
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = {
    "coss-ui": {
        "skill": "coss-ui/official/coss/apps/ui/skills/coss",
        "name": "coss",
        "license": "coss-ui/official/coss/LICENSE",
        "design": [],
        "note": "Use the official coss registry and Tailwind CSS v4/Base UI installation guidance.",
    },
    "heroui": {
        "skill": "heroui/official/heroui/skills/heroui-react",
        "name": "heroui-react",
        "design": [("heroui/official/heroui/apps/docs/public/react/DESIGN.md", "DESIGN.md")],
        "note": "This skill and DESIGN.md are for HeroUI v3 React.",
    },
    "atlassian": {
        "skill": "atlassian/official/atlassian-mcp-server/skills/atlassian-design",
        "name": "atlassian-design",
        "license": "atlassian/official/atlassian-mcp-server/LICENSE",
        "design": [],
        "note": "The public skill targets artifacts/prototypes. For production use the official ADS docs, CLI and MCP; see the README for the official DESIGN.md links and terms.",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("system", choices=SYSTEMS)
    parser.add_argument("project", type=Path, help="An existing target project directory")
    parser.add_argument("--with-design", action="store_true", help="Also copy the system's official DESIGN.md files, where available")
    args = parser.parse_args()
    spec = SYSTEMS[args.system]
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        parser.error("project must be an existing directory")
    if args.with_design and not spec["design"]:
        parser.error(f"{args.system} has no configured official DESIGN.md")
    source = ROOT / spec["skill"]
    destination = project / ".agents" / "skills" / spec["name"]
    license_source = ROOT / spec["license"] if "license" in spec else None
    if license_source and (source / "UPSTREAM-LICENSE").exists():
        raise FileExistsError(f"The official skill already contains UPSTREAM-LICENSE: {source}")
    if license_source and not license_source.is_file():
        raise FileNotFoundError(f"Official license is missing: {license_source}")
    files = [(ROOT / source_path, project / dest_name) for source_path, dest_name in spec["design"]] if args.with_design else []
    for src, dest in [(source, destination), *files]:
        if not src.exists():
            raise FileNotFoundError(f"Official source is missing: {src}")
        if dest.exists() or dest.is_symlink():
            raise FileExistsError(f"Destination already exists; refusing to overwrite: {dest}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    print(f"Copied official skill to {destination}")
    if license_source:
        with license_source.open("rb") as src_file, (destination / "UPSTREAM-LICENSE").open("xb") as dest_file:
            shutil.copyfileobj(src_file, dest_file)
        print("Included the official upstream license alongside the skill.")
    for src, dest in files:
        with src.open("rb") as source_file, dest.open("xb") as destination_file:
            shutil.copyfileobj(source_file, destination_file)
        shutil.copystat(src, dest)
        print(f"Copied official file to {dest}")
    print(spec["note"])
    print("Read the collection README for source versions, licenses, and package setup.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OSError as error:
        print(f"Could not copy official files: {error}", file=sys.stderr)
        sys.exit(1)
