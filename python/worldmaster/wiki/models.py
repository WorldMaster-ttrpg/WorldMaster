from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, cast

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import models
from django.shortcuts import get_object_or_404
from worldmaster.roles.models import Role, RoleTargetBase, RoleTargetManager

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser, AnonymousUser
    from django.http import QueryDict

User = get_user_model()

def _load_int(value: str) -> int | None:
    """Load an integer if the string is not empty, otherwise None."""
    if value:
        return int(value)
    return None

class Article(RoleTargetBase, models.Model):
    """Represents a Wiki article."""

    id: int | None

    sections: models.Manager[Section]

    objects: RoleTargetManager[Article] = RoleTargetManager()

    def update_sections(self, user: AbstractUser | AnonymousUser, data: QueryDict):
        """Update this article's sections using a POST dictionary."""
        if not self.role_target.user_is_editor(user):
            msg = "User can not edit wiki"
            raise PermissionDenied(msg)

        # Not a set or dict because None may appear multiple times
        section_ids = tuple(map(_load_int, data.getlist("wiki-section-id")))

        section_orders = map(float, data.getlist("wiki-section-order"))
        sections = map(json.loads, data.getlist("wiki-section-body"))

        # Get the present IDs so we can delete absent sections (which have been
        # deleted)
        present_ids = {id for id in section_ids if id is not None}

        section_set = self.sections.all()

        for id, order, body in zip(section_ids, section_orders, sections, strict=True):
            section: Section
            if id is None:
                section = section_set.create(
                    order=order,
                    body=body,
                    article=self,
                )

                kwargs = {
                    "user": user,
                    "type": Role.Type.EDITOR,
                    "target": section.role_target,
                }
                if not Role.objects.filter(**kwargs).exists():
                    Role.objects.create(**kwargs)

                present_ids.add(cast(Any, section).id)
            else:
                section = get_object_or_404(Section, id=id)
                if section.role_target.user_is_editor(user):
                    section.body = body
                    section.order = order
                    section.save()

        # Delete removed sections, if the user can delete them.
        for section in section_set.exclude(id__in=present_ids):
            if section.role_target.user_is_editor(user):
                section.delete()

class Section(RoleTargetBase, models.Model):
    """Represents a part of a Wiki article."""

    id: int | None

    article: models.ForeignKey[Article, Article] = models.ForeignKey(
        Article,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="sections",
        related_query_name="section",
    )

    body = models.JSONField(
        blank=False,
        null=False,
        help_text="Article section content",
        default=list,
    )

    # Order is in a range from 0 to the number of sections on the article.
    # Clients might not be able to see all the sections, but can still do
    # alright at preventing totally mangling an article as they edit it.
    order = models.FloatField(help_text="Section order in its article.", blank=False, null=False, default=0.0)

    objects: RoleTargetManager[Section] = RoleTargetManager()

    def __str__(self):
        return str(self.body)

    def __repr__(self):
        return f"<Section: {self.body!r}>"

    class Meta(RoleTargetBase.Meta):
        indexes = [
            models.Index(fields=("article", "order")),
        ]

        ordering = ("article", "order")

class ArticleBase(models.Model):
    """An abstract base that gives an article field to a model."""

    article: models.OneToOneField[Article, Article] = models.OneToOneField(
        Article,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="+",
    )

    class Meta:
        abstract = True
