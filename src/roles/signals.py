from typing import Any, Iterable, cast
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.db import models
from .models import RoleTarget, Role

def _propagate_recursive(instance: RoleTarget) -> None:
    '''Helper function to allow granting roles to targets in a hierarchy without
    having to save the other RoleTargets.
    '''
    parent: RoleTarget | None = instance.parent
    if parent is not None:
        changed = False
        # Create all recursive roles on this.
        for type in Role._RECURSIVE:
            for (user_id,) in Role.objects.filter(
                target=parent,
                type=type,
            ).values_list('user_id'):
                kwargs = {
                    'target': instance,
                    'type': type,
                    'user_id': user_id,
                }

                if not Role.objects.filter(**kwargs).exists():
                    Role.objects.create(**kwargs)
                    changed = True
        if changed:
            for child in cast(Iterable[RoleTarget], cast(Any, instance).children.all()):
                _propagate_recursive(child)

@receiver(post_save, sender=RoleTarget)
def propagate_recursive_roles(
    sender: type[models.Model],
    instance: RoleTarget,
    **kwargs: Any,
) -> None:
    '''Update recursive roles down the chain from this, from the parent down.
    '''
    _propagate_recursive(instance)

@receiver(post_save, sender=Role)
def auto_grant_roles(
    sender: type[models.Model],
    instance: Role,
    **kwargs: Any,
) -> None:
    '''Also grant all auto_grant roles.
    '''
    for auto_grant in Role._AUTO_GRANT[instance.type]:
        kwargs = {
            'user': instance.user,
            'target': instance.target,
            'type': auto_grant,
        }

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
    for role, grants in Role._AUTO_GRANT.items():
        if instance.type != role and instance.type in grants:
            other = Role.objects.filter(
                user=instance.user,
                target=instance.target,
                type=role,
            ).first()

            if other is not None:
                other.delete()
