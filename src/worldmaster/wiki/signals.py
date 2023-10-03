from typing import Any
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import Article, Section
from worldmaster.roles.models import RoleTarget, RoleTargetBase

@receiver(pre_save, sender=Article)
def add_article_role_target(
    sender: type[models.Model],
    instance: Article,
    raw: bool,
    **kwargs: Any,
) -> None:
    '''Add the role_target where appropriate.
    '''
    if not raw and instance.pk is None and not hasattr(instance, 'role_target'):
        instance.role_target = RoleTarget.objects.create()

@receiver(pre_save, sender=Section)
def add_section_role_target(
    sender: type[models.Model],
    instance: Section,
    raw: bool,
    **kwargs: Any,
) -> None:
    '''Add the role_target where appropriate.

    Also associate the parent appropriately.
    '''
    if not raw and instance.pk is None and not hasattr(instance, 'role_target'):
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
    '''Delete the role_target where appropriate and possible.
    '''
    try:
        instance.role_target.delete()
    except models.RestrictedError:
        # Something else is using the role_target.
        pass
