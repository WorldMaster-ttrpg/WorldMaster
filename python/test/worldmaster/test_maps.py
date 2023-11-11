from __future__ import annotations

from django.contrib.gis.geos import Point, Polygon
from django.test import TestCase
from worldmaster.maps.models import Presence
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
            world=self.world,
        )

        self.alpha: Entity = Entity.objects.create(
            slug="alpha",
            name="Alpha",
            world=self.world,
        )
        self.beta: Entity = Entity.objects.create(
            slug="beta",
            name="Beta",
            world=self.world,
        )
        self.gamma: Entity = Entity.objects.create(
            slug="gamma",
            name="Gamma",
            world=self.world,
        )
        self.delta: Entity = Entity.objects.create(
            slug="delta",
            name="Delta",
            world=self.world,
        )

    def test_alpha_in_beta(self):
        Presence.objects.create(
            entity=self.alpha,
            plane=self.plane,
            shape=Polygon((
                (1, 1),
                (1, -1),
                (-1, -1),
                (-1, 1),
                (1, 1),
            )),
            position=Point(0, 0, 0),
        )
        Presence.objects.create(
            entity=self.beta,
            plane=self.plane,
            shape=Polygon((
                (2, 2),
                (2, -2),
                (-2, -2),
                (-2, 2),
                (2, 2),
            )),
            position=Point(0, 0, 0),
        )

