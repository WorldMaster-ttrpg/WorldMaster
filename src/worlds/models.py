from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.template.defaultfilters import slugify
from django.urls import reverse
from typing import Protocol
from worldmaster.validators import validate_not_reserved
from wiki.models import Article, ArticleBase

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

class World(Timestamped, Slugged, ArticleBase):
    '''The top-level model for a setting, representing an entire game setting,
    including all planes, and encompassing all history.

    "World" does not mean the same thing as "planet", but is closer to
    "multiverse".
    '''

    description = models.TextField(null=False, blank=True, default='')

    class Meta(Timestamped.Meta, Slugged.Meta, ArticleBase.Meta):
        constraints = [
            models.UniqueConstraint(fields=['slug'], name='unique_world_slug'),
        ]

    def get_absolute_url(self) -> str:
        return reverse('worlds:world', kwargs={'world_slug': self.slug})

    def __str__(self) -> str:
        return self.slug

class Plane(Timestamped, Slugged, ArticleBase):
    '''A single dimension, with a set of entities set in physical coordinates.

    This is a single physical universe.
    '''

    world = models.ForeignKey(World, null=False, blank=False, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(null=False, blank=True, default='')

    class Meta(Timestamped.Meta, Slugged.Meta, ArticleBase.Meta):
        constraints = [
            models.UniqueConstraint(fields=['world', 'slug'], name='unique_plane_world_slug'),
        ]

    def get_absolute_url(self) -> str:
        return reverse('worlds:plane', kwargs={'world_slug': self.world.slug, 'plane_slug': self.slug})

    def __str__(self) -> str:
        return self.slug

class Entity(Timestamped, Slugged, ArticleBase):
    '''Something that exists somewhere.

    This is for people, places, things, domains, and the like.
    '''

    world = models.ForeignKey(World, null=False, blank=False, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(Timestamped.Meta, Slugged.Meta, ArticleBase.Meta):
        constraints = [
            models.UniqueConstraint(fields=['world', 'slug'], name='unique_entity_world_slug'),
        ]

    def get_absolute_url(self) -> str:
        return reverse('worlds:entity', kwargs={'world_slug': self.world.slug, 'entity_slug': self.slug})

    def __str__(self) -> str:
        return self.slug

class Event(Timestamped, Slugged, ArticleBase):
    '''Something that happens for a particular length of time at a specific location.
    '''

    world = models.ForeignKey(World, null=False, blank=False, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(Timestamped.Meta, Slugged.Meta, ArticleBase.Meta):
        constraints = [
            models.UniqueConstraint(fields=['world', 'slug'], name='unique_event_world_slug'),
        ]

    def get_absolute_url(self) -> str:
        return reverse('worlds:event', kwargs={'world_slug': self.world.slug, 'event_slug': self.slug})

    def __str__(self) -> str:
        return self.slug