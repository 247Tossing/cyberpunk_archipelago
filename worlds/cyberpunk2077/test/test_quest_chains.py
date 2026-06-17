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
        self.assertEqual(edges["Main - Search and Destroy"], "Main - Down on the Street")
        self.assertEqual(
            edges["Point of No Return - Nocturne Op55N1"],
            ("Main - Transmission", "Main - Life During Wartime", "Main - Search and Destroy"),
        )

    def test_badlands_region_and_location_gate(self) -> None:
        edges = get_active_location_prerequisites(self.world)
        self.assertEqual(edges["Main - Ghost Town"], "Main - Playing for Time")
        ghost_town = next(data for data in location_table.values() if data.display_name == "Main - Ghost Town")
        self.assertIn("Badlands", ghost_town.regions)


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

