from typing import Any
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import World, Plane, Entity, Event
from wiki.models import Article
from roles.models import RoleTarget

@receiver(pre_save, sender=World)
def add_world_article_and_share_role_target(
    sender: type[models.Model],
    instance: World,
    raw: bool,
    **kwargs: Any,
) -> None:
    '''Add the article where appropriate, and set up the role_target to share.
    '''
    if instance.pk is None and not hasattr(instance, 'article'):
        article = Article.objects.create()
        instance.article = article
        instance.role_target = article.role_target

@receiver(pre_save, sender=Plane)
@receiver(pre_save, sender=Entity)
@receiver(pre_save, sender=Event)
def add_nonworld_article_and_share_role_target(
    sender: type[models.Model],
    instance: Plane | Entity | Event,
    raw: bool,
    **kwargs: Any,
) -> None:
    '''Add the article where appropriate, and set up the role_target to share.

    This also sets up the RoleTarget parent as expected.

    Note that the role_target parent of all these objects is the World alone.
    An entity exists in a plane, but it may also cross planes, so it only makes
    sense for its parent to be the world.
    '''
    if instance.pk is None and not hasattr(instance, 'article'):
        article = Article.objects.create(
            role_target=RoleTarget.objects.create(
                parent=instance.world.role_target,
            )
        )
        instance.article = article
        instance.role_target = article.role_target

@receiver(post_delete, sender=World)
@receiver(post_delete, sender=Plane)
@receiver(post_delete, sender=Entity)
@receiver(post_delete, sender=Event)
def delete_role_target(
    sender: type[models.Model],
    instance: World | Plane | Entity | Event,
    **kwargs: Any,
) -> None:
    '''Delete the role_target where appropriate and possible.
    '''
    try:
        instance.role_target.delete()
    except models.RestrictedError:
        # Something else is using the role_target.
        pass

@receiver(post_delete, sender=World)
@receiver(post_delete, sender=Plane)
@receiver(post_delete, sender=Entity)
@receiver(post_delete, sender=Event)
def delete_article(
    sender: type[models.Model],
    instance: World | Plane | Entity | Event,
    **kwargs: Any,
) -> None:
    '''Delete the article.
    '''
    instance.article.delete()
