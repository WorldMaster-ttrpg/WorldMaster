from collections.abc import Iterable, Mapping
from typing import Any, cast

from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Role, RoleTarget

# A map from a Role type to all the Role types that it implicitly-grants.
# Role.Types don't include themselves.
# A signal automatically grants the sub-roles.
_SUB: Mapping[Role.Type, frozenset[Role.Type]] = {
    Role.Type.MASTER: frozenset((Role.Type.EDITOR, Role.Type.VIEWER)),
    Role.Type.EDITOR: frozenset((Role.Type.VIEWER,)),
    Role.Type.VIEWER: frozenset(),
}

# Roles that are inherited from parent roletargets.
_INHERITED: frozenset[Role.Type] = frozenset((
    Role.Type.MASTER,
))

# TODO:
# RoleTarget and Role need to handle:
# pre_save and post_delete to remove implicit roles.
# post_save to add implicit roles.

@receiver(post_save, sender=RoleTarget)
def take_parent_inherited_roles(
    sender: type[models.Model],
    instance: RoleTarget,
    raw: bool,
    **kwargs: Any,
) -> None:
    """Update recursive roles down the chain from this, from the parent down.

    This is applied when this role is saved, because the parent may have been
    changed.
    """
    if not raw:
        parent: RoleTarget | None = instance.parent
        if parent is not None:
            for user_id, type in Role.objects.filter(
                target=parent,
                type__in=_INHERITED,
            ).values_list("user_id", "type"):
                kwargs = {
                    "target": instance,
                    "type": type,
                    "user_id": user_id,
                }

                if not Role.objects.filter(**kwargs).exists():
                    # This will trigger the Role post_save signal to recursively
                    # apply downward
                    Role.objects.create(explicit=False, **kwargs)

@receiver(post_save, sender=Role)
def sub_grant_roles(
    sender: type[models.Model],
    instance: Role,
    raw: bool,
    **kwargs: Any,
) -> None:
    """Also grant all auto_grant roles.
    """
    if not raw:
        for auto_grant in _SUB[instance.type]:
            kwargs = {
                "user": instance.user,
                "target": instance.target,
                "type": auto_grant,
            }

            if not Role.objects.filter(**kwargs).exists():
                Role.objects.create(explicit=False, **kwargs)

@receiver(post_save, sender=Role)
def recursive_grant_role(
    sender: type[models.Model],
    instance: Role,
    raw: bool,
    **kwargs: Any,
) -> None:
    """When a recursive role is granted, grant it to the child as well.
    """
    if not raw and instance.type in _INHERITED:
        for child in cast(Iterable[RoleTarget], cast(Any, instance.target).children.all()):
            kwargs = {
                "target": child,
                "type": instance.type,
                "user": instance.user,
            }

            # Granting this will also cause the child to be granted, recursively.
            if not Role.objects.filter(**kwargs).exists():
                Role.objects.create(**kwargs)

@receiver(post_delete, sender=Role)
def auto_remove_roles(
    sender: type[models.Model],
    instance: Role,
    **kwargs: Any,
) -> None:
    """Also remove all granting roles.
    """
    for role, grants in _SUB.items():
        if instance.type != role and instance.type in grants:
            other = Role.objects.filter(
                user=instance.user,
                target=instance.target,
                type=role,
            ).first()

            if other is not None:
                other.delete()
