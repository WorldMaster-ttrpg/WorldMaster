from contextlib import suppress
from typing import Any

from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from worldmaster.roles.models import RoleTarget, RoleTargetBase

from .models import Article, Section


@receiver(pre_save, sender=Article)
def add_article_role_target(
    sender: type[models.Model],
    instance: Article,
    raw: bool,
    **kwargs: Any,
) -> None:
    """Add the role_target where appropriate."""
    if not raw and instance.pk is None and not hasattr(instance, "role_target"):
        instance.role_target = RoleTarget.objects.create()

@receiver(pre_save, sender=Section)
def add_section_role_target(
    sender: type[models.Model],
    instance: Section,
    raw: bool,
    **kwargs: Any,
) -> None:
    """Add the role_target where appropriate.

    Also associate the parent appropriately.
    """
    if not raw and instance.pk is None and not hasattr(instance, "role_target"):
        instance.role_target = RoleTarget.objects.create(
            parent=instance.article.role_target,
        )

@receiver(post_delete, sender=Article)
@receiver(post_delete, sender=Section)
def delete_role_target(
    sender: type[models.Model],
    instance: RoleTargetBase,
    **kwargs: Any,
) -> None:
    """Delete the role_target where appropriate and possible."""
    # Something else may be using the role_target.
    with suppress(models.RestrictedError):
        instance.role_target.delete()
