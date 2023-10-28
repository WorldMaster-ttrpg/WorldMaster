from __future__ import annotations

from typing import Any

from django.db import models
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from .models import Role, RoleTarget


@receiver(post_save, sender=RoleTarget)
def role_target_post_save(
    sender: type[models.Model],
    instance: RoleTarget,
    raw: bool,
    **kwargs: Any,
) -> None:
    """Inherit roles

    This is applied when this role is saved, because the parent may have been
    changed.
    """
    if not raw:
        instance._setup_implicit_roles()

@receiver(pre_delete, sender=RoleTarget)
def role_target_pre_delete(
    sender: type[models.Model],
    instance: RoleTarget,
    **kwargs: Any,
) -> None:
    """Delete all implicit roles from this role target and its children recursively.
    """
    instance._delete_implicit_roles()

@receiver(pre_save, sender=RoleTarget)
def role_target_pre_save(
    sender: type[models.Model],
    instance: RoleTarget,
    raw: bool,
    **kwargs: Any,
) -> None:
    """Delete all implicit roles from this role target and its children
    recursively if it is being re-parented.
    """
    if not raw and instance.id is not None:
        db_instance = RoleTarget.objects.get(id=instance.id)

        if instance.parent != db_instance.parent:
            instance._delete_implicit_roles()

@receiver(post_save, sender=Role)
def role_post_save(
    sender: type[models.Model],
    instance: Role,
    raw: bool,
    **kwargs: Any,
) -> None:
    """Grant implicit roles from a saved role.
    """
    if not raw:
        for child in instance.target.children.all():
            Role.objects.get_or_create(
                target=child,
                type=instance.type,
                user=instance.user,
                defaults={
                    "explicit": False,
                },
            )
        for sub in Role._SUB[instance.type]:
            Role.objects.get_or_create(
                user=instance.user,
                target=instance.target,
                type=sub,
                defaults={
                    "explicit": False,
                },
            )

@receiver(pre_save, sender=Role)
def role_pre_save(
    sender: type[models.Model],
    instance: Role,
    raw: bool,
    **kwargs: Any,
) -> None:
    """Delete all implicit roles for the target so they can be recalculated, unless this is a new record.
    """
    if not raw and instance.id is not None:
        instance.target._delete_implicit_roles()

@receiver(pre_delete, sender=Role)
def role_pre_delete(
    sender: type[models.Model],
    instance: Role,
    **kwargs: Any,
) -> None:
    """Delete all implicit roles for the target so they can be recalculated.
    """
    instance.target._delete_implicit_roles()
