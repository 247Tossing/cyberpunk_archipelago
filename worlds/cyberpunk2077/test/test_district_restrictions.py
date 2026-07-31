from .bases import Cyberpunk2077TestBase


class TestDistrictRestrictions(Cyberpunk2077TestBase):
    options = {
        "district_restriction_type": 1,
        "district_restrict_westbrook": 1,
        "district_restrict_santo_domingo": 1,
    }

    def test_westbrook_requires_token(self) -> None:
        self.assertFalse(self.can_reach_region("Westbrook"))
        self.collect_by_name("Westbrook Access Token")
        self.assertTrue(self.can_reach_region("Westbrook"))

    def test_multi_region_location_requires_all_gated_districts(self) -> None:
        self.collect_by_name("Westbrook Access Token")
        self.assertFalse(self.can_reach_location("Main - Disasterpiece"))

        self.collect_by_name("Santo Domingo Access Token")
        self.assertTrue(self.can_reach_location("Main - Disasterpiece"))

