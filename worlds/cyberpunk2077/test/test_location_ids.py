"""Keep published location IDs identical to the 0.7.5 map after retiring checks."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from ..locations import location_name_groups, location_name_to_id, location_table, retired_location_ids
from ..tools.generate_poptracker_pack import build_locations
from .. import locations as locations_mod
from .bases import Cyberpunk2077TestBase

# Display names removed from generation in 0.7.6. The snapshot still has them,
# at the IDs main assigned before this change.
REMOVED_DISPLAY_NAMES = (
    "Little China Melee Vendor (2) 1",
    "Little China Melee Vendor (2) 2",
    "Little China Melee Vendor (2) 3",
)
REMOVED_INTERNAL_KEYS = (
    "VendorCheck_WatLchMelee02_1",
    "VendorCheck_WatLchMelee02_2",
    "VendorCheck_WatLchMelee02_3",
)

SNAPSHOT_PATH = Path(__file__).with_name("location_name_to_id_0_7_5.json")


def _load_snapshot() -> dict[str, int]:
    raw = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    return {str(name): int(loc_id) for name, loc_id in raw.items()}


class TestRetiredLittleChinaMeleeIds(unittest.TestCase):
    def test_published_ids_match_0_7_5_minus_removed_names(self) -> None:
        snapshot = _load_snapshot()
        for name in REMOVED_DISPLAY_NAMES:
            self.assertIn(name, snapshot)

        expected = {
            name: loc_id
            for name, loc_id in snapshot.items()
            if name not in REMOVED_DISPLAY_NAMES
        }
        actual = {name: int(loc_id) for name, loc_id in location_name_to_id.items()}
        self.assertEqual(actual, expected)

        reserved = {snapshot[name] for name in REMOVED_DISPLAY_NAMES}
        self.assertTrue(reserved.isdisjoint(actual.values()))
        self.assertEqual(
            retired_location_ids,
            {key: snapshot[location_table[key].display_name] for key in REMOVED_INTERNAL_KEYS},
        )
        # Neighbors on either side of the hole keep the IDs they had on main.
        self.assertEqual(actual["Little China Melee Vendor (Coach Fred) 3"], 2077411)
        self.assertEqual(actual["Japantown Melee Vendor (Spector Cheng) 1"], 2077415)
        self.assertEqual(reserved, {2077412, 2077413, 2077414})

    def test_removed_names_leave_groups_counts_and_poptracker(self) -> None:
        for group_name, names in location_name_groups.items():
            for removed in REMOVED_DISPLAY_NAMES:
                self.assertNotIn(removed, names, group_name)

        for key in REMOVED_INTERNAL_KEYS:
            row = location_table[key]
            self.assertTrue(row.retired)
            self.assertIsNone(row.code)
            self.assertNotIn(key, location_name_to_id)
            self.assertNotIn(row.display_name, location_name_to_id)

        melee_names = [
            data.display_name
            for data in location_table.values()
            if data.vendor_subtype == "melee" and not data.retired
        ]
        self.assertEqual(len(melee_names), 18)
        self.assertEqual(len(location_name_to_id), len(_load_snapshot()) - len(REMOVED_DISPLAY_NAMES))

        _defs, mapping, groups = build_locations(locations_mod)
        tracker_names = [name for entries in groups.values() for _code, name in entries]
        for removed in REMOVED_DISPLAY_NAMES:
            self.assertNotIn(removed, tracker_names)
        reserved_ids = {retired_location_ids[key] for key in REMOVED_INTERNAL_KEYS}
        self.assertTrue(reserved_ids.isdisjoint(mapping))


class TestMeleeVendorGenerationOmitsRetiredChecks(Cyberpunk2077TestBase):
    """Vendor Sanity + melee vendors must not roll the unreachable Little China stall."""

    run_default_tests = False
    options = {
        "vendor_sanity": 1,
        "vendor_ripperdocs": 1,
        "vendor_gunsmiths": 1,
        "vendor_clothing": 1,
        "vendor_melee": 1,
        "vendor_netrunners": 1,
        "include_phantom_liberty_dlc": 1,
        "completion_goal": 1,
    }

    def test_retired_melee_checks_are_not_created(self) -> None:
        names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        for removed in (*REMOVED_DISPLAY_NAMES, *REMOVED_INTERNAL_KEYS):
            self.assertNotIn(removed, names)

        melee = sorted(name for name in names if "Melee Vendor" in name)
        self.assertEqual(len(melee), 18)
        self.assertIn("Little China Melee Vendor (Coach Fred) 1", melee)
        self.assertNotIn("Little China Melee Vendor (2) 1", melee)

        stock = str(self.world.fill_slot_data()["vendor_sanity_stock"])
        self.assertNotIn("WatLchMelee02", stock)
        self.assertIn("WatLchMelee01", stock)
