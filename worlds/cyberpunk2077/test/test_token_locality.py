from unittest import TestCase

from Fill import distribute_items_restrictive
from test.general import gen_steps, setup_multiworld
from worlds.AutoWorld import call_all
from worlds.generic.Rules import locality_rules

from .. import Cyberpunk2077World
from ..items import item_name_groups
from ..options import (
    WeaponRestrictionType,
    apply_token_locality_options,
    get_active_district_token_names,
    get_active_weapon_pass_names,
)
from .bases import Cyberpunk2077TestBase


class TestActiveTokenHelpers(Cyberpunk2077TestBase):
    run_default_tests = False
    options = {
        "district_restriction_type": 1,
        "district_restrict_westbrook": 1,
        "district_restrict_santo_domingo": 1,
        "district_restrict_city_center": 0,
        "district_restrict_heywood": 0,
        "district_restrict_pacifica": 0,
        "district_restrict_badlands": 0,
        "district_restrict_dogtown": 0,
    }

    def test_active_district_token_names_match_gated_districts(self) -> None:
        names = get_active_district_token_names(self.world)
        self.assertEqual(
            names,
            {"Westbrook Access Token", "Santo Domingo Access Token"},
        )

    def test_weapon_passes_require_multiworld_item_mode(self) -> None:
        self.assertEqual(get_active_weapon_pass_names(self.world), set())

        self.world.options.weapon_restriction_type.value = WeaponRestrictionType.option_requireMultiworldItem
        self.world.options.weapon_restrict_pistol.value = 1
        self.world.options.weapon_restrict_smg.value = 1

        names = get_active_weapon_pass_names(self.world)
        self.assertEqual(names, {"Pistol Weapon Pass", "SMG Weapon Pass"})


class TestApplyTokenLocalityOptions(Cyberpunk2077TestBase):
    run_default_tests = False
    options = {
        "district_restriction_type": 1,
        "district_restrict_westbrook": 1,
        "district_restrict_city_center": 0,
        "district_restrict_heywood": 0,
        "district_restrict_santo_domingo": 0,
        "district_restrict_pacifica": 0,
        "district_restrict_badlands": 0,
        "district_restrict_dogtown": 0,
        "district_tokens_from_other_worlds": 1,
        "weapon_passes_from_other_worlds": 1,
        "weapon_restriction_type": WeaponRestrictionType.option_requireMultiworldItem,
        "weapon_restrict_pistol": 1,
    }

    def test_default_toggles_populate_non_local_items(self) -> None:
        self.assertIn("Westbrook Access Token", self.world.options.non_local_items.value)
        self.assertIn("Pistol Weapon Pass", self.world.options.non_local_items.value)

    def test_disabled_toggles_leave_non_local_empty(self) -> None:
        self.world.options.district_tokens_from_other_worlds.value = 0
        self.world.options.weapon_passes_from_other_worlds.value = 0
        self.world.options.non_local_items.value = set()

        apply_token_locality_options(self.world)

        self.assertEqual(self.world.options.non_local_items.value, set())


class TestTokenLocalityMultiworld(TestCase):
    options = {
        "district_restriction_type": 1,
        "district_restrict_westbrook": 1,
        "district_restrict_santo_domingo": 1,
        "district_restrict_city_center": 0,
        "district_restrict_heywood": 0,
        "district_restrict_pacifica": 0,
        "district_restrict_badlands": 0,
        "district_restrict_dogtown": 0,
        "district_tokens_from_other_worlds": 1,
        "weapon_restriction_type": WeaponRestrictionType.option_requireMultiworldItem,
        "weapon_restrict_pistol": 1,
        "weapon_passes_from_other_worlds": 1,
    }

    def setUp(self) -> None:
        self.multiworld = setup_multiworld(
            [Cyberpunk2077World, Cyberpunk2077World],
            (),
            seed=0,
            options=self.options,
        )
        for step in gen_steps:
            call_all(self.multiworld, step)
            if step == "set_rules" and self.multiworld.players > 1:
                locality_rules(self.multiworld)
        distribute_items_restrictive(self.multiworld)

    def test_district_tokens_not_placed_on_own_world(self) -> None:
        district_tokens = set(item_name_groups["District Tokens"])
        for location in self.multiworld.get_filled_locations():
            item = location.item
            if item is None or item.player != location.player:
                continue
            with self.subTest(location=location.name, item=item.name):
                self.assertNotIn(item.name, district_tokens)

    def test_weapon_passes_not_placed_on_own_world(self) -> None:
        weapon_passes = set(item_name_groups["Weapon Passes"])
        for location in self.multiworld.get_filled_locations():
            item = location.item
            if item is None or item.player != location.player:
                continue
            with self.subTest(location=location.name, item=item.name):
                self.assertNotIn(item.name, weapon_passes)
