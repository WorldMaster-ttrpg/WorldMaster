from __future__ import annotations

from typing import Any

from django.db import models
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver

from .models import Role, RoleTarget


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
    if not (raw or created):
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
        # This will need to be changed if there are any other save modifications
        # that could invalidate roles.
        db_instance = RoleTarget.objects.get(id=instance.id)

        if instance.parent != db_instance.parent:
            instance._delete_implicit_roles()

@receiver(post_save, sender=Role)
def role_post_save(
    sender: type[models.Model],
    instance: Role,
    raw: bool,
    created: bool,
    **kwargs: Any,
) -> None:
    """Grant implicit roles from a saved role.
    """
    if not raw:
        if created:
            if instance.type in Role._INHERITED:
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
        else:
            # We already deleted everything.
            instance.target._setup_implicit_roles()

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
    if not raw and instance.id is not None:
        # Don't delete self.
        instance.target._delete_implicit_roles(exclude=instance)


@receiver(pre_delete, sender=Role)
def role_pre_delete(
    sender: type[models.Model],
    instance: Role,
    **kwargs: Any,
) -> None:
    """Delete all implicit roles for the target so they can be recalculated.
    """
    if instance.explicit:
        # Don't delete self.
        instance.target._delete_implicit_roles(exclude=instance)

@receiver(post_delete, sender=Role)
def role_post_delete(
    sender: type[models.Model],
    instance: Role,
    **kwargs: Any,
) -> None:
    """Delete all implicit roles for the target so they can be recalculated.
    """
    if instance.explicit:
        instance.target._setup_implicit_roles()
