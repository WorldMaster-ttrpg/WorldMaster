from typing import Any, TypeVar
from django.db import models
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Player, World, Plane, Entity, Event
from wiki.models import Article
from roles.models import Role, RoleTarget

@receiver(pre_save, sender=World)
def add_world_article_and_share_role_target(
    sender: type[World],
    instance: World,
    raw: bool,
    **kwargs: Any,
) -> None:
    '''Add the article where appropriate, and set up the role_target to share.
    '''
    if not raw and instance.pk is None and not hasattr(instance, 'article'):
        article = Article.objects.create()
        instance.article = article
        instance.role_target = article.role_target

PlaneEntityEvent = TypeVar('PlaneEntityEvent', Plane, Entity, Event)

@receiver(pre_save, sender=Plane)
@receiver(pre_save, sender=Entity)
@receiver(pre_save, sender=Event)
def add_nonworld_article_and_share_role_target(
    sender: type[PlaneEntityEvent],
    instance: PlaneEntityEvent,
    raw: bool,
    **kwargs: Any,
) -> None:
    '''Add the article where appropriate, and set up the role_target to share.

    This also sets up the RoleTarget parent as expected.

    Note that the role_target parent of all these objects is the World alone.
    An entity exists in a plane, but it may also cross planes, so it only makes
    sense for its parent to be the world.
    '''
    if not raw and instance.pk is None and not hasattr(instance, 'article'):
        article = Article.objects.create(
            role_target=RoleTarget.objects.create(
                parent=instance.world.role_target,
            )
        )
        instance.article = article
        instance.role_target = article.role_target

WorldPlaneEntityEvent = TypeVar('WorldPlaneEntityEvent', World, Plane, Entity, Event)

@receiver(post_delete, sender=World)
@receiver(post_delete, sender=Plane)
@receiver(post_delete, sender=Entity)
@receiver(post_delete, sender=Event)
def delete_role_target(
    sender: type[WorldPlaneEntityEvent],
    instance: WorldPlaneEntityEvent,
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
    sender: type[WorldPlaneEntityEvent],
    instance: WorldPlaneEntityEvent,
    **kwargs: Any,
) -> None:
    '''Delete the article.
    '''
    instance.article.delete()

@receiver(post_save, sender=Player)
def add_viewer_role_to_player(
    sender: type[Player],
    instance: Player,
    created: bool,
    raw: bool,
    **kwargs,
):
    '''Make sure that any player on a world has view access to at least that world.
    '''
    if not raw:
        kwargs = {
            'target': instance.world.role_target,
            'type': Role.Type.VIEWER,
            'user_id': instance.user.id,
        }

        if not Role.objects.filter(**kwargs).exists():
            Role.objects.create(**kwargs)
