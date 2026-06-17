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

