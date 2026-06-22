from __future__ import annotations

import unittest
from collections.abc import Iterable

from test.general import setup_multiworld

from .. import Cyberpunk2077World
from ..locations import get_regular_locations, location_table
from ..rules import PrereqAny, Prerequisite, get_active_location_prerequisites


def _iter_prereq_names(required: Prerequisite) -> Iterable[str]:
    if isinstance(required, PrereqAny):
        return required.names
    if isinstance(required, tuple):
        return required
    return (required,)


def _find_cycles(edges: dict[str, Prerequisite]) -> list[list[str]]:
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []
    cycles: list[list[str]] = []

    def dfs(node: str) -> None:
        if node in visiting:
            idx = stack.index(node)
            cycles.append(stack[idx:] + [node])
            return
        if node in visited:
            return

        visiting.add(node)
        stack.append(node)
        for dep in _iter_prereq_names(edges.get(node, ())):
            if dep in edges:
                dfs(dep)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in edges:
        dfs(node)
    return cycles


class TestLocationGraph(unittest.TestCase):
    @staticmethod
    def _edges_for_options(options: dict[str, object]) -> dict[str, Prerequisite]:
        multiworld = setup_multiworld([Cyberpunk2077World], options=[options])
        world = multiworld.worlds[1]
        return get_active_location_prerequisites(world)

    def test_default_goal_has_no_cycles(self) -> None:
        cycles = _find_cycles(self._edges_for_options({}))
        self.assertFalse(cycles, f"Found cycles in default prerequisites: {cycles}")

    def test_all_side_quests_goal_has_no_cycles(self) -> None:
        cycles = _find_cycles(self._edges_for_options({"completion_goal": 1}))
        self.assertFalse(cycles, f"Found cycles in side-quests prerequisites: {cycles}")

    def test_phantom_liberty_goal_has_no_cycles(self) -> None:
        cycles = _find_cycles(self._edges_for_options({"completion_goal": 2}))
        self.assertFalse(cycles, f"Found cycles in PL-only prerequisites: {cycles}")

    def test_prerequisite_targets_exist(self) -> None:
        multiworld = setup_multiworld([Cyberpunk2077World], options=[{}])
        world = multiworld.worlds[1]
        edges = get_active_location_prerequisites(world)
        location_names = set(world.location_name_to_id)
        location_names.update(
            data.display_name for data in location_table.values() if data.code is not None
        )
        location_names.update({loc.name for loc in multiworld.get_locations(1)})
        for child, required in edges.items():
            self.assertIn(child, location_names, f"Unknown location in prerequisites: {child}")
            for dep in _iter_prereq_names(required):
                self.assertIn(dep, location_names, f"Unknown prerequisite location: {dep}")

    def test_removed_data_quests_are_not_regular_locations(self) -> None:
        self.assertNotIn("mq033_tarot", location_table)
        self.assertNotIn("mq043_cyberpsychos", location_table)
        regular_ids = set(get_regular_locations())
        self.assertNotIn("mq033_tarot", regular_ids)
        self.assertNotIn("mq043_cyberpsychos", regular_ids)

    def test_mapp_tann_pelen_depends_on_automatic_love_chain(self) -> None:
        edges = self._edges_for_options({})
        self.assertEqual(edges["Main - M'ap Tann Pèlen"], "Main - Double Life")
        self.assertEqual(edges["Main - Double Life"], "Main - Disasterpiece")
        self.assertEqual(edges["Main - Disasterpiece"], "Main - The Space in Between")
        self.assertEqual(edges["Main - The Space in Between"], "Main - Automatic Love")

