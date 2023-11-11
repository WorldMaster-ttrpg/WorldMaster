from __future__ import annotations

from typing import Any

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from worldmaster.roles.models import Role, RoleTarget
from worldmaster.wiki.models import Article

from .models import Entity, Plane, Player, World


@receiver(pre_save, sender=World)
def add_world_article_and_share_role_target(
    sender: type[World],
    instance: World,
    raw: bool,
    **kwargs: Any,
) -> None:
    """Add the article where appropriate, and set up the role_target to share."""
    if not raw and instance.pk is None and not hasattr(instance, "article"):
        article = Article.objects.create()
        instance.article = article
        instance.role_target = article.role_target

@receiver(pre_save, sender=Plane)
@receiver(pre_save, sender=Entity)
def add_nonworld_article_and_share_role_target(
    sender: type[Plane] | type[Entity],
    instance: Plane | Entity,
    raw: bool,
    **kwargs: Any,
) -> None:
    """Add the article where appropriate, and set up the role_target to share.

    This also sets up the RoleTarget parent as expected.

    Note that the role_target parent of all these objects is the World alone.
    An entity exists in a plane, but it may also cross planes, so it only makes
    sense for its parent to be the world.
    """
    if not raw and instance.pk is None and not hasattr(instance, "article"):
        article = Article.objects.create(
            role_target=RoleTarget.objects.create(
                parent=instance.world.role_target,
            ),
        )
        instance.article = article
        instance.role_target = article.role_target

@receiver(post_save, sender=Player)
def add_viewer_role_to_player(
    sender: type[Player],
    instance: Player,
    created: bool,
    raw: bool,
    **kwargs,
):
    """Make sure that any player on a world has view access to at least that world."""
    if not raw:
        kwargs = {
            "target": instance.world.role_target,
            "type": Role.Type.VIEWER,
            "user_id": instance.user.id,
        }

        if not Role.objects.filter(**kwargs).exists():
            Role.objects.create(**kwargs)
