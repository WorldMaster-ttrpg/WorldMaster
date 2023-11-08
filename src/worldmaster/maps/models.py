from __future__ import annotations

from django.contrib.gis.db import models
from django.db.models import F, Q
from worldmaster.worlds.models import Entity, Plane

from . import functions


class Presence(models.Model):
    """An entity presence on the map of a plane.

    This can be time-constrained or timeless.
    """

    entity: models.ForeignKey[Entity, Entity] = models.ForeignKey(
        Entity,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )

    plane: models.ForeignKey[Plane, Plane] = models.ForeignKey(
        Plane,
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

    shape = models.PolygonField(
        "The 2D shape of the presence, with implicit Z coordinates of 0",
        null=False,
        blank=False,
        dim=2,
        srid=0,
    )

    height = models.FloatField(
       "The height of this presence",
       blank=False,
       null=False,
       default=0.0,
    )

    position = models.PointField(
        "The position, or the starting position if end_position is set",
        null=False,
        blank=False,
        dim=3,
        srid=0,
    )

    end_position = models.PointField(
        "The end position, if the presence moved",
        null=True,
        blank=True,
        default=None,
        dim=3,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(start_time__isnull=True) | Q(end_time__isnull=True) | Q(end_time__gt=F("start_time")),
                name="end_time_after_start_time",
                violation_error_message="If start_time and end_time exist, end_time must be greater than start_time.",
            ),
            models.CheckConstraint(
                check=Q(end_position__isnull=True) | Q(start_time__isnull=False) & Q(end_time__isnull=False),
                name="end_position_needs_time_span",
                violation_error_message="If end_position is not null, then start_time and end_time must not be null.",
            ),
            models.CheckConstraint(
                check=~Q(end_position=F("position")),
                name="end_position_different_from_start",
                violation_error_message="end_position must not equal position.",
            ),
            models.CheckConstraint(
                check=functions.IsPolygonCW(F("shape")),
                name="shape_must_be_clockwise",
                violation_error_message="Shapes must be clockwise.",
            ),
        ]
