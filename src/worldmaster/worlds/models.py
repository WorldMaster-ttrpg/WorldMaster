from __future__ import annotations

from typing import TypeVar

from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
from django.urls import reverse

from worldmaster.roles.models import RoleTargetBase, RoleTargetManager
from worldmaster.wiki.models import ArticleBase
from worldmaster.worldmaster.validators import validate_not_reserved

User = get_user_model()

class Timestamped(models.Model):
    """Abstract model for timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Slugged(models.Model):
    """Gives a model a name and a slug."""

    name = models.CharField(
        null=False,
        blank=False,
        max_length=256,
        validators=[MinLengthValidator(3)],
    )

    slug = models.SlugField(
        null=False,
        blank=False,
        # Unique is false, because most inheriters will want a compound
        # uniqueness constraint.
        unique=False,
        max_length=256,
        validators=[MinLengthValidator(3), validate_not_reserved],
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.slug}>"

    class Meta:
        abstract = True

class WorldManager(RoleTargetManager["World"]):
    def get_by_natural_key(self, slug: str) -> World:
        return self.get(slug=slug)

class World(
    Timestamped,
    Slugged,
    ArticleBase,
    RoleTargetBase,
    models.Model,
):
    """Represents an entire game setting.

    "World" does not mean the same thing as "planet", but is closer to
    "universe".
    """

    players = models.ManyToManyField(
        User,
        related_name="worlds",
        related_query_name="world",
        through="Player",
        through_fields=("world", "user"),
    )

    objects = WorldManager()

    # Need this, otherwise the Article.world relation conflicts with the parent
    # relations like Plane.world and such.

    class Meta(Timestamped.Meta, Slugged.Meta, ArticleBase.Meta, RoleTargetBase.Meta):
        constraints = [
            models.UniqueConstraint(fields=["slug"], name="unique_world_slug"),
        ]

    def get_absolute_url(self) -> str:
        return reverse("worlds:world", kwargs={"world_slug": self.slug})

    def natural_key(self) -> tuple[str]:
        return (self.slug,)

class Player(models.Model):
    """A junction table to manage what users are players of a world."""

    world = models.ForeignKey(
        World,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["world", "user"], name="unique_player_world_user"),
        ]

Model = TypeVar("Model", bound="WorldChild")

class WorldChildManager(RoleTargetManager[Model]):
    def get_by_natural_key(self, world_slug, slug) -> Model:
        return self.get(world__slug=world_slug, slug=slug)

class WorldChild(
    Timestamped,
    Slugged,
    ArticleBase,
    RoleTargetBase,
    models.Model,
):
    """A model that's the child of a world."""

    world = models.ForeignKey(
        World,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )

    def natural_key(self) -> tuple[str, str]:
        return (self.world.slug, self.slug)

    class Meta(
        Timestamped.Meta,
        Slugged.Meta,
        ArticleBase.Meta,
        RoleTargetBase.Meta,
    ):
        abstract = True

        constraints = [
            models.UniqueConstraint(fields=["world", "slug"], name="unique_%(class)s_world_slug"),
        ]

class Plane(WorldChild):
    """A single dimension, with a set of entities set in physical coordinates.

    This is a single physical universe.
    """

    objects: WorldChildManager[Plane] = WorldChildManager()

    def get_absolute_url(self) -> str:
        return reverse("worlds:plane", kwargs={"world_slug": self.world.slug, "plane_slug": self.slug})

    def __str__(self) -> str:
        return self.slug

class Entity(WorldChild):
    """Something that exists somewhere.

    This is for people, places, things, domains, and the like.
    """

    objects: WorldChildManager[Entity] = WorldChildManager()

    def get_absolute_url(self) -> str:
        return reverse("worlds:entity", kwargs={"world_slug": self.world.slug, "entity_slug": self.slug})

    def __str__(self) -> str:
        return self.slug

class Event(WorldChild):
    """Something that happens for a particular length of time at a specific location."""

    objects: WorldChildManager[Event] = WorldChildManager()

    def get_absolute_url(self) -> str:
        return reverse("worlds:event", kwargs={"world_slug": self.world.slug, "event_slug": self.slug})

    def __str__(self) -> str:
        return self.slug
