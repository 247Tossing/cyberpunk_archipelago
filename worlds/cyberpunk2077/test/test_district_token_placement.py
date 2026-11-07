"""District-token placement after the sphere-1 early-fill regression.

The deterministic seeds here are the same ones used to compare releases 0.7.2,
0.7.3, and 0.7.4. A broader 400-seed stress run is documented in the pull
request; it is intentionally not part of the unit suite.
"""

from __future__ import annotations

import random
import unittest
from argparse import Namespace
from collections import Counter

from BaseClasses import CollectionState, LocationProgressType, MultiWorld
from Fill import FillError, balance_multiworld_progression, distribute_items_restrictive
from Options import StartInventoryPool
from worlds import AutoWorld
from worlds.generic.Rules import exclusion_rules, locality_rules

from .. import Cyberpunk2077World


def _generate(players: int, options: dict, seed: int) -> MultiWorld:
    """Run the same stages as Generate.py through progression balancing."""
    worlds = [Cyberpunk2077World for _ in range(players)]
    multiworld = MultiWorld(players)
    multiworld.game = {player: world_type.game for player, world_type in enumerate(worlds, 1)}
    multiworld.player_name = {player: f"P{player}" for player in multiworld.player_ids}
    multiworld.set_seed(seed)
    random.seed(multiworld.seed)

    args = Namespace()
    for player, world_type in enumerate(worlds, 1):
        for key, option in world_type.options_dataclass.type_hints.items():
            updated = getattr(args, key, {})
            updated[player] = option.from_any(options.get(key, option.default))
            setattr(args, key, updated)
    multiworld.set_options(args)
    multiworld.state = CollectionState(multiworld)

    AutoWorld.call_all(multiworld, "generate_early")
    for player in multiworld.player_ids:
        world = multiworld.worlds[player]
        for item_name, count in world.options.start_inventory.value.items():
            for _ in range(count):
                multiworld.push_precollected(multiworld.create_item(item_name, player))
        from_pool = getattr(world.options, "start_inventory_from_pool", StartInventoryPool({})).value
        for item_name, count in from_pool.items():
            for _ in range(count):
                multiworld.push_precollected(multiworld.create_item(item_name, player))
    if multiworld.players == 1:
        multiworld.worlds[1].options.non_local_items.value = set()
        multiworld.worlds[1].options.local_items.value = set()

    AutoWorld.call_all(multiworld, "create_regions")
    AutoWorld.call_all(multiworld, "create_items")
    AutoWorld.call_all(multiworld, "set_rules")
    for player in multiworld.player_ids:
        world = multiworld.worlds[player]
        exclusion_rules(multiworld, player, world.options.exclude_locations.value)
        world.options.priority_locations.value -= world.options.exclude_locations.value
    if multiworld.players > 1:
        locality_rules(multiworld)
    AutoWorld.call_all(multiworld, "connect_entrances")
    AutoWorld.call_all(multiworld, "generate_basic")
    _remove_start_inventory_from_pool(multiworld)

    AutoWorld.call_all(multiworld, "pre_fill")
    distribute_items_restrictive(multiworld, "swap")
    if multiworld.players > 1:
        balance_multiworld_progression(multiworld)
    return multiworld


def _remove_start_inventory_from_pool(multiworld: MultiWorld) -> None:
    fallback = StartInventoryPool({})
    depletion = {
        player: dict(getattr(multiworld.worlds[player].options, "start_inventory_from_pool", fallback).value)
        for player in multiworld.player_ids
    }
    if not any(depletion.values()):
        return
    kept = []
    for item in multiworld.itempool:
        if depletion[item.player].get(item.name, 0):
            depletion[item.player][item.name] -= 1
        else:
            kept.append(item)
    for player, counts in depletion.items():
        removed = sum(
            getattr(multiworld.worlds[player].options, "start_inventory_from_pool", fallback).value.values()
        ) - sum(counts.values())
        kept.extend(multiworld.worlds[player].create_filler() for _ in range(removed))
    assert len(kept) == len(multiworld.itempool)
    multiworld.itempool[:] = kept


def _token_spheres(multiworld: MultiWorld) -> list[tuple[int, str, int, int]]:
    rows: list[tuple[int, str, int, int]] = []
    sphere_index = 0
    unreachable = False
    for sphere in multiworld.get_spheres():
        if not sphere:
            unreachable = True
            continue
        if not unreachable:
            sphere_index += 1
        for location in sphere:
            item = location.item
            if item is None or not item.advancement or not item.name.endswith(" Access Token"):
                continue
            rows.append((sphere_index, item.name, item.player, location.player))
    return rows


def _assert_not_blanket_sphere1(test: unittest.TestCase, rows: list[tuple[int, str, int, int]]) -> None:
    test.assertTrue(rows)
    test.assertFalse(all(sphere == 1 for sphere, *_ in rows))


def _assert_no_early_requests(test: unittest.TestCase, multiworld: MultiWorld) -> None:
    for player in multiworld.player_ids:
        for name in multiworld.early_items[player]:
            test.assertFalse(name.endswith(" Access Token"), name)


class TestBuiltinPriorityAndEarlyFill(unittest.TestCase):
    def test_gated_builtin_priority_is_released_and_open_priority_stays(self) -> None:
        multiworld = _generate(2, {"district_restriction_type": 1}, seed=1)
        _assert_no_early_requests(self, multiworld)
        for player in (1, 2):
            self.assertEqual(
                multiworld.get_location("Prologue - Love Like Fire", player).progress_type,
                LocationProgressType.PRIORITY,
            )
            self.assertEqual(
                multiworld.get_location("Main - Transmission", player).progress_type,
                LocationProgressType.DEFAULT,
            )
            self.assertEqual(
                multiworld.get_location("Point of No Return - Nocturne Op55N1", player).progress_type,
                LocationProgressType.DEFAULT,
            )

    def test_explicit_reachable_priority_receives_progression(self) -> None:
        multiworld = _generate(
            2,
            {
                "district_restriction_type": 1,
                "priority_locations": ["Prologue - Love Like Fire"],
            },
            seed=1,
        )
        for player in (1, 2):
            location = multiworld.get_location("Prologue - Love Like Fire", player)
            self.assertEqual(location.progress_type, LocationProgressType.PRIORITY)
            self.assertIsNotNone(location.item)
            self.assertTrue(location.item.advancement)

    def test_explicit_satisfiable_gated_priority_is_kept(self) -> None:
        multiworld = _generate(
            2,
            {
                "district_restriction_type": 1,
                "priority_locations": ["Main - Search and Destroy"],
            },
            seed=1,
        )
        for player in (1, 2):
            location = multiworld.get_location("Main - Search and Destroy", player)
            self.assertEqual(location.progress_type, LocationProgressType.PRIORITY)
            self.assertIsNotNone(location.item)
            self.assertTrue(location.item.advancement)
            self.assertNotEqual(location.item.player, location.player)
        rows = _token_spheres(multiworld)
        _assert_not_blanket_sphere1(self, rows)

    def test_explicit_priority_that_requires_every_token_is_a_clear_error(self) -> None:
        with self.assertRaises(FillError) as caught:
            _generate(
                2,
                {
                    "district_restriction_type": 1,
                    "priority_locations": ["Point of No Return - Nocturne Op55N1"],
                },
                seed=1,
            )
        message = str(caught.exception)
        self.assertIn("Point of No Return - Nocturne Op55N1", message)
        self.assertIn("priority_locations", message)


class TestDistrictTokenDistribution(unittest.TestCase):
    def test_two_player_other_worlds_on_seeds_1_through_5(self) -> None:
        for seed in range(1, 6):
            with self.subTest(seed=seed):
                multiworld = _generate(2, {"district_restriction_type": 1}, seed=seed)
                rows = _token_spheres(multiworld)
                self.assertEqual(len(rows), 12)
                _assert_not_blanket_sphere1(self, rows)
                _assert_no_early_requests(self, multiworld)
                for sphere, _name, item_player, location_player in rows:
                    self.assertNotEqual(item_player, location_player)
                    self.assertGreaterEqual(sphere, 1)
                multiworld.spoiler.create_playthrough(create_paths=False)
                self.assertIn("Victory", str(multiworld.spoiler.playthrough))

    def test_locality_off_seeds_1_through_3(self) -> None:
        options = {"district_restriction_type": 1, "district_tokens_from_other_worlds": 0}
        for seed in range(1, 4):
            with self.subTest(seed=seed):
                multiworld = _generate(2, options, seed=seed)
                rows = _token_spheres(multiworld)
                self.assertEqual(len(rows), 12)
                _assert_not_blanket_sphere1(self, rows)

    def test_solo_seeds_1_through_3_are_local(self) -> None:
        for seed in range(1, 4):
            with self.subTest(seed=seed):
                multiworld = _generate(1, {"district_restriction_type": 1}, seed=seed)
                rows = _token_spheres(multiworld)
                self.assertEqual(len(rows), 6)
                _assert_not_blanket_sphere1(self, rows)
                for _sphere, _name, item_player, location_player in rows:
                    self.assertEqual(item_player, location_player)

    def test_phantom_liberty_adds_dogtown_without_sphere1_collapse(self) -> None:
        options = {"district_restriction_type": 1, "include_phantom_liberty_dlc": 1}
        for seed in (1, 2):
            with self.subTest(seed=seed):
                multiworld = _generate(2, options, seed=seed)
                rows = _token_spheres(multiworld)
                self.assertEqual(len(rows), 14)
                self.assertTrue(any(name.startswith("Dogtown ") for _s, name, _i, _l in rows))
                _assert_not_blanket_sphere1(self, rows)
                for _s, _n, item_player, location_player in rows:
                    self.assertNotEqual(item_player, location_player)

    def test_weapon_passes_do_not_reintroduce_early_token_requests(self) -> None:
        options = {
            "district_restriction_type": 1,
            "weapon_restriction_type": 2,
            "weapon_restrict_pistol": 1,
            "weapon_restrict_rifle": 1,
        }
        for seed in (1, 2):
            with self.subTest(seed=seed):
                multiworld = _generate(2, options, seed=seed)
                rows = _token_spheres(multiworld)
                _assert_not_blanket_sphere1(self, rows)
                _assert_no_early_requests(self, multiworld)
                passes = [
                    location.item
                    for location in multiworld.get_filled_locations()
                    if location.item and location.item.name.endswith(" Weapon Pass")
                ]
                self.assertEqual(len(passes), 4)
                for item in passes:
                    self.assertNotEqual(item.player, item.location.player)

    def test_subdistrict_tokens_generate_and_are_not_all_sphere1(self) -> None:
        multiworld = _generate(
            2,
            {"district_restriction_type": 1, "restrict_by_sub_district": 1},
            seed=1,
        )
        rows = _token_spheres(multiworld)
        self.assertGreater(len(rows), 12)
        _assert_not_blanket_sphere1(self, rows)
        self.assertTrue(any("Japantown" in name for _s, name, _i, _l in rows))

    def test_start_inventory_token_opens_its_district(self) -> None:
        # Archipelago 0.6.8's common options expose start_inventory, which adds
        # a precollected copy and still leaves the rolled copy in the pool.
        multiworld = _generate(
            1,
            {
                "district_restriction_type": 1,
                "start_inventory": {"Westbrook Access Token": 1},
            },
            seed=1,
        )
        precollected = [item.name for item in multiworld.precollected_items[1]]
        self.assertIn("Westbrook Access Token", precollected)
        state = CollectionState(multiworld)
        self.assertTrue(multiworld.get_region("Westbrook", 1).can_reach(state))
        _assert_no_early_requests(self, multiworld)
        rows = _token_spheres(multiworld)
        self.assertGreaterEqual(len(rows), 6)
        _assert_not_blanket_sphere1(self, rows)


class TestSphereSpreadShape(unittest.TestCase):
    def test_seed1_two_player_matches_recorded_shape(self) -> None:
        multiworld = _generate(2, {"district_restriction_type": 1}, seed=1)
        counts = Counter(sphere for sphere, *_ in _token_spheres(multiworld))
        # Natural fill, not a scripted sphere schedule: record the seed-1 shape
        # so a return of the early-item collapse (12 tokens in sphere 1) fails.
        self.assertEqual(dict(counts), {1: 6, 2: 5, 3: 1})
        multiworld.spoiler.create_playthrough(create_paths=False)
        play_counts: Counter[str] = Counter()
        for sphere, entries in multiworld.spoiler.playthrough.items():
            if not isinstance(entries, dict):
                continue
            for item_name in entries.values():
                if " Access Token" in str(item_name):
                    play_counts[sphere] += 1
        self.assertEqual({int(key): value for key, value in play_counts.items()}, {1: 6, 2: 5, 3: 1})
