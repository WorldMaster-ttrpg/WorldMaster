from __future__ import annotations

from typing import Any

from django.db import models
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver

from .models import Role, RoleTarget


def _set_previous_target(role: Role) -> None:
    """Set _previous_target if explicit."""
    if role.explicit:
        if role.id is None:
            role._previous_target = None
        else:
            role._previous_target = Role.objects.get(id=role.id).target

def _rebuild_role_targets(role: Role) -> None:
    """Rebuild target and _previous_target if explicit."""
    if role.explicit:
        previous_target = role._previous_target
        target = role.target
        if previous_target is not None and previous_target != target:
            previous_target._rebuild_roles()
        target._rebuild_roles()

@receiver(post_save, sender=RoleTarget)
def role_target_post_save(
    sender: type[models.Model],
    instance: RoleTarget,
    raw: bool,
    created: bool,
    **kwargs: Any,
) -> None:
    """Inherit roles

    This is applied when this role is saved, because the parent may have been
    changed.
    """
    if not raw:
        instance._rebuild_roles()

@receiver(pre_save, sender=Role)
def role_pre_save(
    sender: type[models.Model],
    instance: Role,
    raw: bool,
    **kwargs: Any,
) -> None:
    """Delete all implicit roles for the target so they can be recalculated, unless this is a new record.
    """
    # This could be redundant or wasteful, but it's the easiest way to ensure
    # that we always get consistent roles after a role is moved, deleted, or its
    # type is changed.
    # We could do some logic that crawls implicit roles and only deletes ones
    # that are necessary, but it's not a problem right now, especially for a
    # read-heavy setup.
    if not raw:
        _set_previous_target(instance)

@receiver(pre_delete, sender=Role)
def role_pre_delete(
    sender: type[models.Model],
    instance: Role,
    **kwargs: Any,
) -> None:
    """Delete all implicit roles for the target so they can be recalculated.
    """
    _set_previous_target(instance)

@receiver(post_save, sender=Role)
def role_post_save(
    sender: type[models.Model],
    instance: Role,
    raw: bool,
    created: bool,
    **kwargs: Any,
) -> None:
    """Rebuild roles for the target and the previous target.
    """
    if not raw:
        _rebuild_role_targets(instance)

@receiver(post_delete, sender=Role)
def role_post_delete(
    sender: type[models.Model],
    instance: Role,
    **kwargs: Any,
) -> None:
    """Rebuild roles for the target.
    """
    _rebuild_role_targets(instance)
