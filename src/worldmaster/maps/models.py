from django.contrib.gis.db import models
from worldmaster.worlds.models import Entity


class Presence(models.Model):
    """An entity presence on the map.

    This can be time-constrained or timeless.
    """

    entity: models.ForeignKey[Entity, Entity] = models.ForeignKey(
        Entity,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )

    start_time = models.FloatField(
       "The time that this presence appeared",
       blank=True,
       null=True,
       default=None,
    )

    end_time = models.FloatField(
       "The time that this presence disappeared",
       blank=True,
       null=True,
       default=None,
    )

    shape = models.MultiPolygonField(
        null=False,
        blank=False,
        dim=3,
        geography=False,
    )

    position = models.PointField(
        "The position, or the starting position if end_position is set",
        null=False,
        blank=False,
        dim=3,
        geography=False,
    )

    end_position = models.PointField(
        "The end position, if the presence moved",
        null=True,
        blank=True,
        default=None,
        dim=3,
        geography=False,
    )
