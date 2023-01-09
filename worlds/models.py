from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator

User = get_user_model()

class World(models.Model):
    '''The top-level model for a setting, representing an entire game setting,
    including all planes, and encompassing all history.

    "World" does not mean the same thing as "planet", but is closer to
    "multiverse".
    '''

    # The URL slug for this world
    slug = models.SlugField(db_index=True, unique=True, null=False)
    name = models.TextField(null=False, validators=[MinLengthValidator(3)])
    description = models.TextField(null=False)

    # The owner of the world, with full superuser access.
    game_master = models.ForeignKey(User, null=False, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Plane(models.Model):
    '''A single dimension, with a set of entities set in physical coordinates.

    This is a single physical universe.
    '''

    world = models.ForeignKey(World, on_delete=models.CASCADE)
    slug = models.SlugField(null=False)

    description = models.TextField(null=False)

    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['world', 'slug']),
        ]

