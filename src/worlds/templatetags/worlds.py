from typing import Any
from django import template
from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from roles.models import Role
from worlds.models import World

User = get_user_model()

register = template.Library()

@register.filter
def mastered_worlds(user: Any) -> QuerySet[World]:
    '''Filter a user into its mastered worlds.
    '''
    return World.objects.filter(
        role_target__role__type=Role.Type.MASTER,
        role_target__role__user=user,
    )

    
