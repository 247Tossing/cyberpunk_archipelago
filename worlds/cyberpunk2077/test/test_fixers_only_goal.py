from .bases import Cyberpunk2077TestBase
from ..items import ItemCategory, item_table
from ..locations import (
    FIXER_MAX_TIER,
    FIXER_TIER_STREET_CRED,
    GIG_FIXER_TIERS,
    LocationCategory,
    fixer_tier_item_name,
    location_table,
)

FIXERS_ONLY = {"completion_goal": 3}

GIG_COUNT_BASE = 72
GIG_COUNT_WITH_PHANTOM_LIBERTY = 81


def _categories_in_pool(world) -> set[str]:
    included = {loc.name for loc in world.multiworld.get_locations(world.player) if loc.address is not None}
    return {data.category for data in location_table.values() if data.display_name in included}


class TestFixerTierTable(Cyberpunk2077TestBase):
    options = FIXERS_ONLY

    def test_every_gig_has_a_fixer_tier(self) -> None:
        gig_keys = {name for name, data in location_table.items() if data.category == LocationCategory.GIG}
        self.assertEqual(gig_keys, set(GIG_FIXER_TIERS))

    def test_street_cred_thresholds_cover_every_tier(self) -> None:
        for fixer, max_tier in FIXER_MAX_TIER.items():
            thresholds = FIXER_TIER_STREET_CRED[fixer]
            self.assertEqual(len(thresholds), max_tier, fixer)
            self.assertEqual(thresholds[0], 1, f"{fixer} tier 1 should need no street cred")
            self.assertEqual(sorted(thresholds), list(thresholds), f"{fixer} thresholds must not decrease")

    def test_every_tier_above_the_first_has_an_item(self) -> None:
        for fixer, max_tier in FIXER_MAX_TIER.items():
            for tier in range(2, max_tier + 1):
                name = fixer_tier_item_name(fixer, tier)
                self.assertIn(name, item_table)
                self.assertEqual(item_table[name].category, ItemCategory.FIXER_TIER)


class TestFixersOnlyPool(Cyberpunk2077TestBase):
    options = FIXERS_ONLY

    def test_pool_holds_only_gigs_and_the_prologue_check(self) -> None:
        self.assertEqual(_categories_in_pool(self.world), {LocationCategory.GIG, LocationCategory.MAIN_QUEST})

    def test_gig_count(self) -> None:
        included = {loc.name for loc in self.multiworld.get_locations(self.player)}
        gigs = [data for data in location_table.values()
                if data.category == LocationCategory.GIG and data.display_name in included]
        self.assertEqual(len(gigs), GIG_COUNT_BASE)

    def test_gigs_are_included_even_when_the_toggle_is_off(self) -> None:
        # generate_early forces include_gigs on, since the goal has nothing else.
        self.assertTrue(self.world.options.include_gigs)

    def test_item_pool_fits_the_location_pool(self) -> None:
        locations = [loc for loc in self.multiworld.get_locations(self.player) if loc.address is not None]
        self.assertLessEqual(len(self.multiworld.itempool), len(locations))

    def test_only_needed_fixer_tier_items_are_placed(self) -> None:
        placed = {item.name for item in self.multiworld.itempool
                  if item_table[item.name].category == ItemCategory.FIXER_TIER}
        # Without Phantom Liberty, Mr. Hands only hands out the one Pacifica gig,
        # so his Dogtown tiers have nothing to gate.
        self.assertNotIn(fixer_tier_item_name("hands", 2), placed)
        self.assertNotIn(fixer_tier_item_name("hands", 4), placed)
        self.assertIn(fixer_tier_item_name("regina", 2), placed)

    def test_higher_tier_gigs_need_their_fixer_tier_item(self) -> None:
        # "Fixer, Merc, Soldier, Spy" is Regina's only tier 4 gig.
        gig = location_table["sts_wat_kab_04"].display_name
        self.assertFalse(self.can_reach_location(gig))
        self.collect_by_name(fixer_tier_item_name("regina", 4))
        self.assertTrue(self.can_reach_location(gig))

    def test_first_tier_gigs_need_no_item(self) -> None:
        # "Hippocratic Oath" is a Regina tier 1 gig in Watson, the starting district.
        self.assertTrue(self.can_reach_location(location_table["sts_wat_kab_02"].display_name))

    def test_victory_requires_every_gig(self) -> None:
        self.assertFalse(self.can_reach_location("Victory"))


class TestFixersOnlyPhantomLiberty(Cyberpunk2077TestBase):
    options = {**FIXERS_ONLY, "include_phantom_liberty_dlc": 1}

    def test_dogtown_gigs_are_included(self) -> None:
        included = {loc.name for loc in self.multiworld.get_locations(self.player)}
        gigs = [data for data in location_table.values()
                if data.category == LocationCategory.GIG and data.display_name in included]
        self.assertEqual(len(gigs), GIG_COUNT_WITH_PHANTOM_LIBERTY)

    def test_mr_hands_dogtown_tiers_are_placed(self) -> None:
        placed = {item.name for item in self.multiworld.itempool
                  if item_table[item.name].category == ItemCategory.FIXER_TIER}
        self.assertIn(fixer_tier_item_name("hands", 2), placed)
        self.assertIn(fixer_tier_item_name("hands", 4), placed)


class TestFixersOnlySlotData(Cyberpunk2077TestBase):
    options = FIXERS_ONLY

    def test_manifest_lists_every_included_gig(self) -> None:
        slot_data = self.world.fill_slot_data()
        self.assertEqual(slot_data["completion_goal"], 3)
        manifest = slot_data["gig_goal_manifest"].split(",")
        self.assertEqual(len(manifest), GIG_COUNT_BASE)
        self.assertTrue(all(key in GIG_FIXER_TIERS for key in manifest))


class TestOtherGoalsExcludeFixerTierItems(Cyberpunk2077TestBase):
    options = {"completion_goal": 0}

    def test_no_fixer_tier_items_in_pool(self) -> None:
        placed = [item.name for item in self.multiworld.itempool
                  if item_table[item.name].category == ItemCategory.FIXER_TIER]
        self.assertEqual(placed, [])

    def test_gigs_have_no_tier_requirement(self) -> None:
        # Other goals leave gig availability to vanilla street cred.
        self.assertTrue(self.can_reach_location(location_table["sts_wat_kab_04"].display_name))
