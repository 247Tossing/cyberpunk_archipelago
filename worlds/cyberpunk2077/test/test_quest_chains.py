from .bases import Cyberpunk2077TestBase
from ..locations import location_table
from ..rules import PrereqAny, get_active_location_prerequisites


class TestQuestChains(Cyberpunk2077TestBase):
    run_default_tests = False

    def test_main_chain_prerequisites(self) -> None:
        edges = get_active_location_prerequisites(self.world)
        self.assertEqual(
            edges["Prologue - The Heist"],
            ("Prologue - The Pickup", "Prologue - The Information"),
        )
        self.assertEqual(edges["Main - Search and Destroy"], "Main - Play It Safe")
        self.assertEqual(edges["Main - Automatic Love"], "Main - Playing for Time")
        self.assertEqual(edges["Main - The Space in Between"], "Main - Automatic Love")
        self.assertEqual(edges["Main - Disasterpiece"], "Main - The Space in Between")
        self.assertEqual(edges["Main - Double Life"], "Main - Disasterpiece")
        self.assertEqual(edges["Main - M'ap Tann Pèlen"], "Main - Double Life")
        self.assertEqual(edges["Main - I Walk the Line"], "Main - M'ap Tann Pèlen")
        self.assertEqual(edges["Main - Transmission"], "Main - I Walk the Line")
        self.assertEqual(
            edges["Point of No Return - Nocturne Op55N1"],
            ("Main - Transmission", "Main - Life During Wartime", "Main - Search and Destroy"),
        )

    def test_badlands_region_and_location_gate(self) -> None:
        edges = get_active_location_prerequisites(self.world)
        self.assertEqual(edges["Main - Ghost Town"], "Main - Playing for Time")
        ghost_town = next(data for data in location_table.values() if data.display_name == "Main - Ghost Town")
        self.assertIn("Badlands", ghost_town.regions)

    def test_judy_chain_transitively_requires_automatic_love(self) -> None:
        edges = get_active_location_prerequisites(self.world)
        transitive = self._collect_transitive_prerequisites("Main - M'ap Tann Pèlen", edges)
        self.assertIn("Main - Automatic Love", transitive)

    def test_rogue_chain_stays_on_search_and_destroy_gate(self) -> None:
        self.assertEqual(location_table["sq031_rogue"].prerequisite, "Main - Search and Destroy")
        self.assertEqual(location_table["sq031_cinema"].prerequisite, "Chippin' In")

class TestDelamainEpistrophyPrerequisites(Cyberpunk2077TestBase):
    run_default_tests = False
    options = {
        "completion_goal": 1,
    }

    def test_dont_lose_your_mind_requires_all_epistrophy_checks(self) -> None:
        expected = (
            "Epistrophy",
            "Epistrophy: Wellsprings",
            "Epistrophy: North Oak",
            "Epistrophy: Coastview",
            "Epistrophy: Rancho Coronado",
            "Epistrophy: Northside",
            "Epistrophy: Badlands",
            "Epistrophy: The Glen",
        )
        capstone = location_table["sq025b_delamain_insurgence"]
        self.assertEqual(capstone.prerequisite, expected)

        edges = get_active_location_prerequisites(self.world)
        self.assertEqual(edges["Don't Lose Your Mind"], expected)


class TestPhantomLibertyQuestChains(Cyberpunk2077TestBase):
    run_default_tests = False
    options = {
        "completion_goal": 2,
    }

    def test_phantom_liberty_chain_prerequisites(self) -> None:
        edges = get_active_location_prerequisites(self.world)
        self.assertEqual(
            edges["Phantom Liberty - Firestarter"],
            "Phantom Liberty - I've Seen That Face Before",
        )
        split_prereq = edges["Phantom Liberty - Who Wants to Live Forever"]
        self.assertIsInstance(split_prereq, PrereqAny)
        self.assertEqual(
            split_prereq.names,
            ("PL - Split Quest 1", "PL - Split Quest 2", "PL - Split Quest 3"),
        )


class TestWestbrookTokenSoftlockRegression(Cyberpunk2077TestBase):
    run_default_tests = False
    options = {
        "district_restriction_type": 1,
        "district_restrict_westbrook": 1,
        "district_restrict_badlands": 0,
        "district_restrict_city_center": 0,
        "district_restrict_heywood": 0,
        "district_restrict_santo_domingo": 0,
        "district_restrict_pacifica": 0,
        "district_restrict_dogtown": 0,
    }

    def test_mapp_tann_pelen_not_reachable_before_westbrook_token(self) -> None:
        self.assertFalse(self.can_reach_location("Main - Automatic Love"))
        self.assertFalse(self.can_reach_location("Main - M'ap Tann Pèlen"))

    def test_westbrook_token_unlocks_judy_chain_progression(self) -> None:
        self.collect_by_name("Westbrook Access Token")
        self.assertTrue(self.can_reach_location("Main - Automatic Love"))
        self.assertTrue(self.can_reach_location("Main - M'ap Tann Pèlen"))

