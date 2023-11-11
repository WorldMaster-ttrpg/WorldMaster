from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.db.models import F, Q
from worldmaster.worlds.models import Entity, Plane

if TYPE_CHECKING:
    from worldmaster import shape  # type: ignore

class Presence(models.Model):
    """An entity presence on the map of a plane.

    This can be time-constrained or timeless.
    """

    id: int

    entity: models.ForeignKey[Entity, Entity] = models.ForeignKey(
        Entity,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        db_index=True,
    )

    plane: models.ForeignKey[Plane, Plane] = models.ForeignKey(
        Plane,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        db_index=True,
    )

    start_time = models.BigIntegerField(
       "The time that this presence appeared",
       blank=True,
       null=True,
       default=None,
    )

    end_time = models.BigIntegerField(
       "The time that this presence disappeared",
       blank=True,
       null=True,
       default=None,
    )

    shape = models.BinaryField(
        "The 3D shape of the field",
        null=False,
        blank=False,
    )

    hull = models.BinaryField(
        "The convex hull of the field, swept over time if necessary",
        null=True,
        blank=True,
        default=None,
    )

    x = models.BigIntegerField(
       blank=False,
       null=False,
    )
    y = models.BigIntegerField(
       blank=False,
       null=False,
    )
    z = models.BigIntegerField(
       blank=False,
       null=False,
    )

    end_x = models.BigIntegerField(
       blank=True,
       null=True,
       default=None,
    )
    end_y = models.BigIntegerField(
       blank=True,
       null=True,
       default=None,
    )
    end_z = models.BigIntegerField(
       blank=True,
       null=True,
       default=None,
    )

    min_x = models.BigIntegerField(
       blank=False,
       null=False,
    )
    min_y = models.BigIntegerField(
       blank=False,
       null=False,
    )
    min_z = models.BigIntegerField(
       blank=False,
       null=False,
    )
    max_x = models.BigIntegerField(
       blank=False,
       null=False,
    )
    max_y = models.BigIntegerField(
       blank=False,
       null=False,
    )
    max_z = models.BigIntegerField(
       blank=False,
       null=False,
    )

    @property
    def position(self) -> shape.Vector3D:
        return shape.Vector3D(self.x, self.y, self.z)

    @position.setter
    def position(self, value: shape.Vector3D) -> None:
        self.x = value.x
        self.y = value.y
        self.z = value.z

    @property
    def end_position(self) -> shape.Vector3D:
        return shape.Vector3D(self.end_x, self.end_y, self.end_z)

    @end_position.setter
    def end_position(self, value: shape.Vector3D) -> None:
        self.end_x = value.x
        self.end_y = value.y
        self.end_z = value.z

    class Meta:
        indexes = [
            models.Index(
                name="plane_time_index",
                fields=("plane", "start_time", "end_time"),
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(start_time__isnull=True) | Q(end_time__isnull=True) | Q(end_time__gt=F("start_time")),
                name="end_time_after_start_time",
                violation_error_message="If start_time and end_time exist, end_time must be greater than start_time.",
            ),
            models.CheckConstraint(
                check=Q(end_x__isnull=True) & Q(end_y__isnull=True) & Q(end_z__isnull=True)
                    | Q(end_x__isnull=False) & Q(end_y__isnull=False) & Q(end_z__isnull=False)
                ,
                name="end_position_all_set",
                violation_error_message="The end position coordinates must either be all set or all null",
            ),
            models.CheckConstraint(
                check=Q(end_x__isnull=True) & Q(end_y__isnull=True) & Q(end_z__isnull=True) | Q(start_time__isnull=False) & Q(end_time__isnull=False),
                name="end_position_needs_time_span",
                violation_error_message="If end_position is not null, then start_time and end_time must not be null.",
            ),
            models.CheckConstraint(
                check=~(Q(x=F("end_x")) & Q(y=F("end_y")) & Q(z=F("end_z"))),
                name="end_position_different_from_start",
                violation_error_message="end_position must not equal position.",
            ),
        ]
