from .bases import Cyberpunk2077TestBase


class TestDeathLinkSlotData(Cyberpunk2077TestBase):
    options = {
        "death_link": 1,
        "death_link_amnesty": 3,
    }

    def test_fill_slot_data_deathlink_keys(self) -> None:
        slot_data = self.world.fill_slot_data()
        self.assertTrue(slot_data["death_link"])
        self.assertEqual(slot_data["death_link_amnesty"], 3)
