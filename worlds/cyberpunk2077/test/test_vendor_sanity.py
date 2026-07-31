from BaseClasses import LocationProgressType

from .bases import Cyberpunk2077TestBase
from ..rules import get_active_location_prerequisites


class TestVendorSanityRules(Cyberpunk2077TestBase):
    options = {
        "vendor_sanity": 1,
        "vendor_ripperdocs": 1,
        "vendor_gunsmiths": 0,
        "vendor_clothing": 0,
        "vendor_melee": 0,
        "vendor_netrunners": 0,
    }

    def test_ripperdoc_vendor_edges_are_active(self) -> None:
        edges = get_active_location_prerequisites(self.world)
        self.assertEqual(edges["Victor's Shop 1"], "Prologue - The Ripperdoc")
        self.assertEqual(edges["Downtown Ripperdoc 1"], "Prologue - The Ripperdoc")

    def test_other_vendor_subtypes_are_filtered_out(self) -> None:
        edges = get_active_location_prerequisites(self.world)
        self.assertNotIn("2nd Amendment Shop 1", edges)


# Jackson Plains Ripperdoc Stall 1/2 model the Aldecaldos camp relocation: Stall 1 is the
# pre-move camp ripperdoc (missable once "Queen of the Highway" completes), Stall 2 is the
# post-move camp ripperdoc (only exists once side quests -- and therefore Panam's chain --
# are included in generation).
STALL_1_LOCATION_NAMES = (
    "Jackson Plains Ripperdoc (Stall 1) 1",
    "Jackson Plains Ripperdoc (Stall 1) 2",
    "Jackson Plains Ripperdoc (Stall 1) 3",
)
STALL_2_LOCATION_NAMES = (
    "Jackson Plains Ripperdoc (Stall 2) 1",
    "Jackson Plains Ripperdoc (Stall 2) 2",
    "Jackson Plains Ripperdoc (Stall 2) 3",
)

VENDOR_SANITY_RIPPERDOC_ONLY_OPTIONS = {
    "vendor_sanity": 1,
    "vendor_ripperdocs": 1,
    "vendor_gunsmiths": 0,
    "vendor_clothing": 0,
    "vendor_melee": 0,
    "vendor_netrunners": 0,
}


class TestJacksonPlainsRipperdocStallsDefaultGoal(Cyberpunk2077TestBase):
    """Default goal has no side quests, so Panam's chain (and the camp move) never happens."""

    run_default_tests = False
    options = {
        **VENDOR_SANITY_RIPPERDOC_ONLY_OPTIONS,
        "completion_goal": 0,
    }

    def test_stall_2_is_not_populated(self) -> None:
        location_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        for name in STALL_2_LOCATION_NAMES:
            self.assertNotIn(name, location_names)

    def test_stall_2_has_no_active_prerequisite_edge(self) -> None:
        edges = get_active_location_prerequisites(self.world)
        for name in STALL_2_LOCATION_NAMES:
            self.assertNotIn(name, edges)

    def test_stall_1_is_populated_and_excluded(self) -> None:
        for name in STALL_1_LOCATION_NAMES:
            location = self.multiworld.get_location(name, self.player)
            self.assertEqual(location.progress_type, LocationProgressType.EXCLUDED)


class TestJacksonPlainsRipperdocStallsAllSideQuestsGoal(Cyberpunk2077TestBase):
    run_default_tests = False
    options = {
        **VENDOR_SANITY_RIPPERDOC_ONLY_OPTIONS,
        "completion_goal": 1,
    }

    def test_stall_2_is_populated(self) -> None:
        location_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        for name in STALL_2_LOCATION_NAMES:
            self.assertIn(name, location_names)

    def test_stall_1_remains_excluded(self) -> None:
        for name in STALL_1_LOCATION_NAMES:
            location = self.multiworld.get_location(name, self.player)
            self.assertEqual(location.progress_type, LocationProgressType.EXCLUDED)

    def test_stall_2_requires_prologue_and_queen_of_the_highway(self) -> None:
        edges = get_active_location_prerequisites(self.world)
        for name in STALL_2_LOCATION_NAMES:
            self.assertEqual(edges[name], ("Prologue - The Ripperdoc", "Queen of the Highway"))

    def test_stall_2_unreachable_without_district_access(self) -> None:
        # Badlands is only reachable via Westbrook or Santo Domingo, both restricted by
        # default -- with no items collected, Stall 2 must be unreachable.
        for name in STALL_2_LOCATION_NAMES:
            self.assertFalse(self.can_reach_location(name))

    def test_stall_2_reachable_once_badlands_access_and_queen_chain_resolve(self) -> None:
        # Collecting only the district tokens needed to physically reach Badlands (no
        # item gates Panam's chain itself) proves the AND-tuple prerequisite resolves
        # end-to-end against real location names, catching typos/broken references.
        self.collect_by_name("Westbrook Access Token")
        self.collect_by_name("Badlands Access Token")
        for name in STALL_2_LOCATION_NAMES:
            self.assertTrue(self.can_reach_location(name))

