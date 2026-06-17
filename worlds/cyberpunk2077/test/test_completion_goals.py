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

