from __future__ import annotations

from django.test import TestCase
from worldmaster.worlds.models import Entity, Plane, World


class MapsTestCase(TestCase):
    def setUp(self) -> None:
        self.world: World = World.objects.create(
            slug="world",
            name="World",
        )
        self.plane: Plane = self.world.plane_set.create(
            slug="plane",
            name="Plane",
        )

        self.alpha: Entity = Entity.objects.create(
            slug="alpha",
            name="Alpha",
        )
        self.beta: Entity = Entity.objects.create(
            slug="beta",
            name="Beta",
        )
        self.gamma: Entity = Entity.objects.create(
            slug="gamma",
            name="Gamma",
        )
        self.delta: Entity = Entity.objects.create(
            slug="delta",
            name="Delta",
        )

    def test_alpha_in_beta(self):
        pass

