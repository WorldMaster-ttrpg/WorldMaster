from typing import Any

from django import template
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from worldmaster.roles.models import Role
from worldmaster.worlds.models import World

User = get_user_model()

register = template.Library()

@register.filter
def mastered_worlds(user: Any) -> QuerySet[World]:
    """Filter a user into its mastered worlds."""
    return World.objects.filter(
        role_target__role__type=Role.Type.MASTER,
        role_target__role__user=user,
    )


