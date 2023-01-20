from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.urls import reverse
from worldmaster.validators import validate_not_reserved

User = get_user_model()

class World(models.Model):
    '''The top-level model for a setting, representing an entire game setting,
    including all planes, and encompassing all history.

    "World" does not mean the same thing as "planet", but is closer to
    "multiverse".
    '''

    # The URL slug for this world
    slug = models.SlugField(
        db_index=True,
        unique=True,
        null=False,
        blank=False,
        max_length=64,
        validators=[MinLengthValidator(3), validate_not_reserved],
    )

    name = models.CharField(
        null=False,
        blank=False,
        max_length=64,
        validators=[MinLengthValidator(3)],
    )
    description = models.TextField(null=False, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self) -> str:
        return reverse('worlds:world', kwargs={'world_slug': self.slug})

class Plane(models.Model):
    '''A single dimension, with a set of entities set in physical coordinates.

    This is a single physical universe.
    '''

    world = models.ForeignKey(World, null=False, blank=False, on_delete=models.CASCADE)

    slug = models.SlugField(
        null=False,
        blank=False,
        max_length=64,
        validators=[MinLengthValidator(3), validate_not_reserved],
    )

    name = models.CharField(
        null=False,
        blank=False,
        max_length=64,
        validators=[MinLengthValidator(3)],
    )

    description = models.TextField(null=False)

    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['world', 'slug'], name='unique_world_slug'),
        ]

    def get_absolute_url(self) -> str:
        return reverse('worlds:plane', kwargs={'world_slug': self.world.slug, 'plane_slug': self.slug})

