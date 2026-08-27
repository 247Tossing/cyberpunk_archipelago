from .bases import Cyberpunk2077TestBase


class TestDefaultEndingGoal(Cyberpunk2077TestBase):
    options = {
        "completion_goal": 0,
    }


class TestAllSideQuestsGoal(Cyberpunk2077TestBase):
    options = {
        "completion_goal": 1,
    }


class TestPhantomLibertyOnlyGoal(Cyberpunk2077TestBase):
    options = {
        "completion_goal": 2,
    }


class TestFixersOnlyGoal(Cyberpunk2077TestBase):
    options = {
        "completion_goal": 3,
    }


class TestFixersOnlyGoalWithPhantomLiberty(Cyberpunk2077TestBase):
    options = {
        "completion_goal": 3,
        "include_phantom_liberty_dlc": 1,
    }


class TestFixersOnlyGoalWithVendorSanity(Cyberpunk2077TestBase):
    options = {
        "completion_goal": 3,
        "vendor_sanity": 1,
        "vendor_ripperdocs": 1,
    }


class TestFixersOnlyGoalWithDistrictTokens(Cyberpunk2077TestBase):
    options = {
        "completion_goal": 3,
        "district_restriction_type": 1,
    }

