"""
Generate a basic PopTracker pack from the Cyberpunk 2077 Archipelago world data.

The generated pack is intentionally list-based: it tracks received AP items and
checked AP locations, but does not include map pins or access logic. The source
of truth remains ``locations.py`` and ``items.py``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Any, Iterable

try:
    from .generate_redscript_ap_mappings import _load_world_modules
except ImportError:  # pragma: no cover - supports direct script execution.
    from generate_redscript_ap_mappings import _load_world_modules  # type: ignore


THIS_FILE = Path(__file__).resolve()
WORLD_DIR = THIS_FILE.parent.parent
MOD_ROOT = WORLD_DIR.parent.parent
WORLD_MANIFEST = WORLD_DIR / "archipelago.json"
PLACEHOLDER_IMG = "images/check.png"
PACKAGE_UID = "cyberpunk2077_ap"
PACKAGE_NAME = "Cyberpunk 2077 AP Tracker"
MIN_POPTRACKER_VERSION = "0.25.2"


def slugify(value: str) -> str:
    """Return a stable PopTracker code fragment for a display/internal name."""
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return slug or "unnamed"


def category_label(value: str) -> str:
    return value.replace("_", " ").title()


def chunked(values: list[str], size: int) -> list[list[str]]:
    return [values[index:index + size] for index in range(0, len(values), size)]


def tracker_code(item_def: dict[str, Any]) -> str:
    if "codes" in item_def:
        return str(item_def["codes"])
    stages = item_def.get("stages", [])
    if stages and "codes" in stages[0]:
        return str(stages[0]["codes"])
    raise ValueError(f"PopTracker item is missing codes: {item_def.get('name', '<unnamed>')}")


def json_item_toggle(name: str, code: str) -> dict[str, Any]:
    return {
        "name": name,
        "type": "toggle",
        "img": PLACEHOLDER_IMG,
        "codes": code,
    }


def json_item_consumable(name: str, code: str, increment: int) -> dict[str, Any]:
    return {
        "name": name,
        "type": "consumable",
        "img": PLACEHOLDER_IMG,
        "codes": code,
        "min_quantity": 0,
        "max_quantity": -1,
        "increment": max(1, int(increment)),
        "decrement": max(1, int(increment)),
        "initial_quantity": 0,
    }


def json_item_progressive(name: str, code: str, quantity: int) -> dict[str, Any]:
    stage_count = max(1, int(quantity))
    return {
        "name": name,
        "type": "progressive",
        "allow_disabled": True,
        "loop": False,
        "stages": [
            {
                "name": f"{name} {stage}/{stage_count}",
                "img": PLACEHOLDER_IMG,
                "codes": code,
            }
            for stage in range(1, stage_count + 1)
        ],
    }


def item_tracker_type(items_mod: Any, item_data: Any) -> str:
    category = item_data.category
    if category == items_mod.ItemCategory.QUICKHACK:
        return "progressive"
    if category in {
        items_mod.ItemCategory.CURRENCY,
        items_mod.ItemCategory.CONSUMABLE,
        items_mod.ItemCategory.TRAP,
    }:
        return "consumable"
    return "toggle"


def build_manifest(version: str) -> dict[str, Any]:
    return {
        "name": PACKAGE_NAME,
        "game_name": "Cyberpunk 2077",
        "package_uid": PACKAGE_UID,
        "package_version": version,
        "author": "247Tossing",
        "variants": {
            "standard": {
                "display_name": "AP Autotracker",
                "flags": ["ap"],
            },
        },
        "min_poptracker_version": MIN_POPTRACKER_VERSION,
        "target_poptracker_version": MIN_POPTRACKER_VERSION,
    }


def build_items(items_mod: Any) -> tuple[list[dict[str, Any]], dict[int, tuple[str, str]]]:
    item_defs: list[dict[str, Any]] = []
    mapping: dict[int, tuple[str, str]] = OrderedDict()

    for display_name, item_data in items_mod.item_table.items():
        if item_data.code is None:
            continue

        code = f"recv_{slugify(display_name)}"
        item_type = item_tracker_type(items_mod, item_data)
        if item_type == "progressive":
            item_defs.append(json_item_progressive(display_name, code, item_data.quantity))
        elif item_type == "consumable":
            item_defs.append(json_item_consumable(display_name, code, item_data.quantity))
        else:
            item_defs.append(json_item_toggle(display_name, code))

        mapping[items_mod.item_name_to_id[display_name]] = (code, item_type)

    return item_defs, mapping


def build_locations(locations_mod: Any) -> tuple[list[dict[str, Any]], dict[int, list[str]], dict[str, list[str]]]:
    location_defs: list[dict[str, Any]] = []
    mapping: dict[int, list[str]] = OrderedDict()
    codes_by_category: dict[str, list[str]] = defaultdict(list)
    seen_wire_ids: set[int] = set()

    for internal_name, location_data in locations_mod.location_table.items():
        if location_data.code is None:
            continue

        wire_id = locations_mod.location_name_to_id.get(location_data.display_name)
        if wire_id is None or wire_id in seen_wire_ids:
            continue
        seen_wire_ids.add(wire_id)

        code = f"chk_{slugify(internal_name)}"
        location_defs.append(json_item_toggle(location_data.display_name, code))
        mapping[wire_id] = [code]
        codes_by_category[category_label(location_data.category)].append(code)

    return location_defs, mapping, dict(codes_by_category)


def make_itemgrid(codes: list[str], *, columns: int) -> dict[str, Any]:
    """Build a PopTracker itemgrid layout node."""
    return {
        "type": "itemgrid",
        "h_alignment": "left",
        "v_alignment": "top",
        "item_size": 40,
        "item_margin": "3, 3",
        "rows": chunked(codes, columns) if codes else [[]],
    }


def build_grids(item_defs: list[dict[str, Any]], location_groups: dict[str, list[str]]) -> dict[str, Any]:
    """Named itemgrid layouts referenced from tracker.json."""
    grids: dict[str, Any] = {
        "items_grid": make_itemgrid([tracker_code(item) for item in item_defs], columns=6),
    }
    for group_name in sorted(location_groups):
        grid_key = f"locations_{slugify(group_name)}"
        grids[grid_key] = make_itemgrid(location_groups[group_name], columns=8)
    return grids


def build_tracker(location_groups: dict[str, list[str]]) -> dict[str, Any]:
    """
    Build the root tracker layout.

    PopTracker expects tracker_default to be a container with a content child.
    Avoid nested tabbed widgets; expose each category as its own top-level tab.
    """
    tabs: list[dict[str, Any]] = [
        {
            "title": "Items",
            "content": {
                "type": "group",
                "header": "Received Items",
                "content": {
                    "type": "layout",
                    "key": "items_grid",
                },
            },
        },
    ]

    for group_name in sorted(location_groups):
        tabs.append(
            {
                "title": group_name,
                "content": {
                    "type": "group",
                    "header": group_name,
                    "content": {
                        "type": "layout",
                        "key": f"locations_{slugify(group_name)}",
                    },
                },
            }
        )

    return {
        "tracker_default": {
            "type": "container",
            "background": "#1b1b1b",
            "content": {
                "type": "tabbed",
                "tabs": tabs,
            },
        },
        "tracker_broadcast": {
            "type": "layout",
            "key": "tracker_default",
        },
    }


def lua_string(value: str) -> str:
    return json.dumps(value)


def render_item_mapping(mapping: dict[int, tuple[str, str]]) -> str:
    lines = [
        "-- AUTO-GENERATED FILE - DO NOT EDIT MANUALLY",
        "-- Source: worlds/cyberpunk2077/items.py",
        "ITEM_MAPPING = {",
    ]
    for item_id, (code, item_type) in mapping.items():
        lines.append(f"    [{item_id}] = {{{lua_string(code)}, {lua_string(item_type)}}},")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def render_location_mapping(mapping: dict[int, list[str]]) -> str:
    lines = [
        "-- AUTO-GENERATED FILE - DO NOT EDIT MANUALLY",
        "-- Source: worlds/cyberpunk2077/locations.py",
        "LOCATION_MAPPING = {",
    ]
    for location_id, codes in mapping.items():
        rendered_codes = ", ".join(lua_string(code) for code in codes)
        lines.append(f"    [{location_id}] = {{{rendered_codes}}},")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8", newline="\n")


def copy_templates(template_dir: Path, output_dir: Path) -> None:
    if not template_dir.is_dir():
        return
    shutil.copytree(template_dir, output_dir, dirs_exist_ok=True)


def generate_pack(output_dir: Path, template_dir: Path | None = None, version_override: str | None = None) -> None:
    locations_mod, items_mod = _load_world_modules()
    version = version_override or str(json.loads(WORLD_MANIFEST.read_text(encoding="utf-8"))["world_version"])

    if template_dir is not None:
        copy_templates(template_dir, output_dir)

    item_defs, item_mapping = build_items(items_mod)
    location_defs, location_mapping, location_groups = build_locations(locations_mod)

    write_json(output_dir / "manifest.json", build_manifest(version))
    write_json(output_dir / "items" / "received_items.json", item_defs)
    write_json(output_dir / "items" / "location_checks.json", location_defs)
    write_json(output_dir / "layouts" / "grids.json", build_grids(item_defs, location_groups))
    write_json(output_dir / "layouts" / "tracker.json", build_tracker(location_groups))
    write_text(output_dir / "scripts" / "autotracking" / "item_mapping.lua", render_item_mapping(item_mapping))
    write_text(
        output_dir / "scripts" / "autotracking" / "location_mapping.lua",
        render_location_mapping(location_mapping),
    )

    print(
        f"[gen_poptracker] wrote {output_dir}  "
        f"(locations: {len(location_mapping)}, items: {len(item_mapping)})"
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a basic Cyberpunk 2077 PopTracker pack."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory to write generated pack files into.",
    )
    parser.add_argument(
        "--template-dir",
        type=Path,
        default=None,
        help="Optional static template directory to copy before generating files.",
    )
    parser.add_argument(
        "--archipelago-root",
        type=Path,
        default=None,
        help="Path to an Archipelago source checkout used to import BaseClasses/world modules.",
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Override package_version in generated manifest.json.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.archipelago_root:
        os.environ["ARCHIPELAGO_ROOT"] = str(args.archipelago_root.resolve())

    generate_pack(
        args.output_dir.resolve(),
        args.template_dir.resolve() if args.template_dir else None,
        args.version,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
