from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.template.defaultfilters import slugify
from django.urls import reverse
from typing import Protocol
from worldmaster.validators import validate_not_reserved

User = get_user_model()

class Sluggable(models.Model):
    slug = models.SlugField(
        null=False,
        blank=False,
        max_length=256,
        validators=[MinLengthValidator(3), validate_not_reserved],
    )

    name = models.CharField(
        null=False,
        blank=False,
        max_length=256,
        validators=[MinLengthValidator(3)],
    )

    class Meta:
        abstract = True

class World(Sluggable):
    '''The top-level model for a setting, representing an entire game setting,
    including all planes, and encompassing all history.

    "World" does not mean the same thing as "planet", but is closer to
    "multiverse".
    '''

    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(Sluggable.Meta):
        constraints = [
            models.UniqueConstraint(fields=['slug'], name='unique_world_slug'),
        ]

    def get_absolute_url(self) -> str:
        return reverse('worlds:world', kwargs={'world_slug': self.slug})

    def __str__(self) -> str:
        return self.slug

class Plane(Sluggable):
    '''A single dimension, with a set of entities set in physical coordinates.

    This is a single physical universe.
    '''

    world = models.ForeignKey(World, null=False, blank=False, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['world', 'slug'], name='unique_plane_world_slug'),
        ]

    def get_absolute_url(self) -> str:
        return reverse('worlds:plane', kwargs={'world_slug': self.world.slug, 'plane_slug': self.slug})

    def __str__(self) -> str:
        return self.slug
