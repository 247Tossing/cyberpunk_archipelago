from __future__ import annotations

from collections import deque
from typing import Iterable

from test.bases import WorldTestBase

from .. import Cyberpunk2077World
from ..rules import PrereqAny, Prerequisite, get_active_location_prerequisites


class Cyberpunk2077TestBase(WorldTestBase):
    game = "Cyberpunk 2077"
    world: Cyberpunk2077World

    def test_all_state_can_reach_everything(self):
        """Cyberpunk override using non-deprecated get_all_state() call."""
        if not (self.run_default_tests and self.constructed):
            return
        with self.subTest("Game", game=self.game, seed=self.multiworld.seed):
            state = self.multiworld.get_all_state()
            for location in self.multiworld.get_locations():
                with self.subTest("Location should be reached", location=location.name):
                    reachable = location.can_reach(state)
                    self.assertTrue(reachable, f"{location.name} unreachable")
            with self.subTest("Beatable"):
                self.multiworld.state = state
                self.assertBeatable(True)

    def assert_location_reachable(self, names: Iterable[str], *, satisfied: bool = True) -> None:
        for name in names:
            self.assertEqual(
                self.can_reach_location(name),
                satisfied,
                f"{name} should {'be reachable' if satisfied else 'not be reachable'}",
            )

    def collect_checked_location(self, location_name: str) -> None:
        location = self.multiworld.get_location(location_name, self.player)
        if location.item is not None:
            self.multiworld.state.collect(location.item, True, location)
        else:
            self.multiworld.state.locations_checked.add(location)

    def assert_prerequisite_order(self, child_location: str, edges: dict[str, Prerequisite] | None = None) -> None:
        if edges is None:
            edges = get_active_location_prerequisites(self.world)

        self.assertIn(child_location, edges, f"Missing prerequisite mapping for {child_location}")

        for prereq in self._collect_transitive_prerequisites(child_location, edges):
            if any(loc.name == prereq for loc in self.multiworld.get_locations(self.player)):
                self.collect_checked_location(prereq)

        self.assertTrue(
            self.can_reach_location(child_location),
            f"{child_location} should be reachable after collecting prerequisite chain",
        )

    @staticmethod
    def _iter_prerequisite_names(required: Prerequisite) -> tuple[str, ...]:
        if isinstance(required, PrereqAny):
            return required.names
        if isinstance(required, tuple):
            return required
        return (required,)

    def _collect_transitive_prerequisites(
        self,
        child_location: str,
        edges: dict[str, Prerequisite],
    ) -> list[str]:
        ordered: list[str] = []
        visited: set[str] = set()
        queue: deque[str] = deque(self._iter_prerequisite_names(edges[child_location]))

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            ordered.append(current)
            if current in edges:
                queue.extend(self._iter_prerequisite_names(edges[current]))

        ordered.reverse()
        return ordered
