from typing import Any

from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from worldmaster.roles.models import RoleTarget

from .models import Article, ArticleBase, Section


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

# Automatically set up article deletion.
# This will not catch any classes that do not exist before this signal is
# registered, or articles that are manually set up without using ArticleBase.
def delete_article(
    sender: type[ArticleBase],
    instance: ArticleBase,
    **kwargs: Any,
) -> None:
    """Delete the article."""
    if instance.article.id is not None:
        instance.article.delete()

def _recursively_connect_children(cls: type[ArticleBase]):
    for subclass in cls.__subclasses__():
        if not subclass._meta.abstract:
            post_delete.connect(delete_article, sender=subclass)
        _recursively_connect_children(subclass)

_recursively_connect_children(ArticleBase)
