from __future__ import annotations

from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.urls import reverse
from worldmaster.validators import validate_not_reserved
from wiki.models import ArticleBase
from roles.models import Role, RoleTargetBase

User = get_user_model()

class Timestamped(models.Model):
    '''Abstract model for timestamps.
    '''
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Slugged(models.Model):
    '''Gives a model a name and a slug.
    '''
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

    class Meta:
        abstract = True

class World(
    Timestamped,
    Slugged,
    ArticleBase,
    RoleTargetBase,
    models.Model,
):
    '''The top-level model for a setting, representing an entire game setting,
    including all planes, and encompassing all history.

    "World" does not mean the same thing as "planet", but is closer to
    "universe" or "multiverse".
    '''

    # Need this, otherwise the Article.world relation conflicts with the parent
    # relations like Plane.world and such.

    class Meta(Timestamped.Meta, Slugged.Meta, ArticleBase.Meta, RoleTargetBase.Meta):
        constraints = [
            models.UniqueConstraint(fields=['slug'], name='unique_world_slug'),
        ]

    def get_absolute_url(self) -> str:
        return reverse('worlds:world', kwargs={'world_slug': self.slug})

    def __str__(self) -> str:
        return self.slug

    @staticmethod
    def visible_to(user: AbstractUser | AnonymousUser) -> models.QuerySet[World]:
        if user.is_superuser:
            return World.objects.all()
        elif user.is_anonymous:
            return World.objects.filter(
                role_target__roles__type=Role.Type.VIEWER,
                role_target__roles__user=None,
            )
        else:
            return World.objects.filter(
                models.Q(role_target__roles__user=None) | models.Q(role_target__roles__user=user),
                role_target__roles__type=Role.Type.VIEWER,
            )

class WorldChild(models.Model):
    '''A model that's the child of a world
    '''
    world = models.ForeignKey(
        World,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True

class Plane(
    WorldChild,
    Timestamped,
    Slugged,
    ArticleBase,
    RoleTargetBase,
    models.Model,
):
    '''A single dimension, with a set of entities set in physical coordinates.

    This is a single physical universe.
    '''

    class Meta(
        WorldChild.Meta,
        Timestamped.Meta,
        Slugged.Meta,
        ArticleBase.Meta,
        RoleTargetBase.Meta,
    ):
        constraints = [
            models.UniqueConstraint(fields=['world', 'slug'], name='unique_plane_world_slug'),
        ]

    def get_absolute_url(self) -> str:
        return reverse('worlds:plane', kwargs={'world_slug': self.world.slug, 'plane_slug': self.slug})

    def __str__(self) -> str:
        return self.slug

    @staticmethod
    def visible_to(user: AbstractUser | AnonymousUser) -> models.QuerySet[Plane]:
        if user.is_superuser:
            return Plane.objects.all()
        elif user.is_anonymous:
            return Plane.objects.filter(
                role_target__roles__type=Role.Type.VIEWER,
                role_target__roles__user=None,
            )
        else:
            return Plane.objects.filter(
                models.Q(role_target__roles__user=None) | models.Q(role_target__roles__user=user),
                role_target__roles__type=Role.Type.VIEWER,
            )

class Entity(
    WorldChild,
    Timestamped,
    Slugged,
    ArticleBase,
    RoleTargetBase,
    models.Model,
):
    '''Something that exists somewhere.

    This is for people, places, things, domains, and the like.
    '''
    class Meta(
        WorldChild.Meta,
        Timestamped.Meta,
        Slugged.Meta,
        ArticleBase.Meta,
        RoleTargetBase.Meta,
    ):
        constraints = [
            models.UniqueConstraint(fields=['world', 'slug'], name='unique_entity_world_slug'),
        ]

    def get_absolute_url(self) -> str:
        return reverse('worlds:entity', kwargs={'world_slug': self.world.slug, 'entity_slug': self.slug})

    def __str__(self) -> str:
        return self.slug

class Event(
    WorldChild,
    Timestamped,
    Slugged,
    ArticleBase,
    RoleTargetBase,
    models.Model,
):
    '''Something that happens for a particular length of time at a specific location.
    '''
    class Meta(
        WorldChild.Meta,
        Timestamped.Meta,
        Slugged.Meta,
        ArticleBase.Meta,
        RoleTargetBase.Meta,
    ):
        constraints = [
            models.UniqueConstraint(fields=['world', 'slug'], name='unique_event_world_slug'),
        ]

    def get_absolute_url(self) -> str:
        return reverse('worlds:event', kwargs={'world_slug': self.world.slug, 'event_slug': self.slug})

    def __str__(self) -> str:
        return self.slug
