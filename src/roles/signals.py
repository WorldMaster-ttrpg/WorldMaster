from collections.abc import Mapping
from typing import Any, Iterable, cast
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.db import models
from .models import RoleTarget, Role

# A map from a Role type to all the Role types that it auto-grants.
# Role.Types don't include themselves.
# A signal automatically grants the sub-roles.
_AUTO_GRANT: Mapping[Role.Type, frozenset[Role.Type]] = {
    Role.Type.MASTER: frozenset((Role.Type.EDITOR, Role.Type.VIEWER)),
    Role.Type.EDITOR: frozenset((Role.Type.VIEWER,)),
    Role.Type.VIEWER: frozenset(),
}

# Roles that apply recursively.
_RECURSIVE: frozenset[Role.Type] = frozenset((
    Role.Type.MASTER,
))

@receiver(post_save, sender=RoleTarget)
def take_parent_recursive_roles(
    sender: type[models.Model],
    instance: RoleTarget,
    raw: bool,
    **kwargs: Any,
) -> None:
    '''Update recursive roles down the chain from this, from the parent down.

    This is applied when this role is saved, because the parent may have been
    changed.
    '''
    if not raw:
        parent: RoleTarget | None = instance.parent
        if parent is not None:
            for user_id, type in Role.objects.filter(
                target=parent,
                type__in=_RECURSIVE,
            ).values_list('user_id', 'type'):
                kwargs = {
                    'target': instance,
                    'type': type,
                    'user_id': user_id,
                }

                if not Role.objects.filter(**kwargs).exists():
                    # This will trigger the Role post_save signal to recursively
                    # apply downward
                    Role.objects.create(**kwargs)

@receiver(post_save, sender=Role)
def auto_grant_roles(
    sender: type[models.Model],
    instance: Role,
    raw: bool,
    **kwargs: Any,
) -> None:
    '''Also grant all auto_grant roles.
    '''
    if not raw:
        for auto_grant in _AUTO_GRANT[instance.type]:
            kwargs = {
                'user': instance.user,
                'target': instance.target,
                'type': auto_grant,
            }

            if not Role.objects.filter(**kwargs).exists():
                Role.objects.create(**kwargs)

@receiver(post_save, sender=Role)
def recursive_grant_role(
    sender: type[models.Model],
    instance: Role,
    raw: bool,
    **kwargs: Any,
) -> None:
    '''When a recursive role is granted, grant it to the child as well.
    '''
    if not raw and instance.type in _RECURSIVE:
        for child in cast(Iterable[RoleTarget], cast(Any, instance.target).children.all()):
            kwargs = {
                'target': child,
                'type': instance.type,
                'user': instance.user,
            }

            # Granting this will also cause the child to be granted, recursively.
            if not Role.objects.filter(**kwargs).exists():
                Role.objects.create(**kwargs)

@receiver(pre_delete, sender=Role)
def auto_remove_roles(
    sender: type[models.Model],
    instance: Role,
    **kwargs: Any,
) -> None:
    '''Also remove all granting roles.
    '''
    for role, grants in _AUTO_GRANT.items():
        if instance.type != role and instance.type in grants:
            other = Role.objects.filter(
                user=instance.user,
                target=instance.target,
                type=role,
            ).first()

            if other is not None:
                other.delete()
