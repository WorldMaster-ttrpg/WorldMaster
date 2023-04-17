from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models.query import QuerySet
from django.http import QueryDict
from django.shortcuts import get_object_or_404
from worldmaster.models import User
from roles.models import Role, RoleTarget, RoleTargetBase

def _load_int(value: str) -> int | None:
    '''Load an integer if the string is not empty, otherwise None.
    '''
    if value:
        return int(value)
    else:
        return None

class Article(RoleTargetBase, models.Model):
    """Represents a Wiki article.
    """

    def sections(self) -> Iterable['Section']:
        '''Get the sections for this article in order.
        '''
        return cast(QuerySet[Section], cast(Any, self).section_set).order_by('order')

    def body_text(self) -> str:
        '''Get the joined text of all the sections of this article..
        '''
        return '\n\n'.join(section.text for section in self.sections())

    def update_sections(self, user: User, data: QueryDict):
        '''Using a POST dictionary, update this article's sections.
        '''

        if not self.role_target.user_can_edit(user):
            raise PermissionDenied('User can not edit wiki')

        # Not a set or dict because None may appear multiple times
        section_ids = tuple(map(_load_int, data.getlist('wiki-section-id')))

        section_orders = map(float, data.getlist('wiki-section-order'))
        sections = data.getlist('wiki-section')

        # Get the present IDs so we can delete absent sections (which have been
        # deleted)
        present_ids = set(id for id in section_ids if id is not None)

        section_set: QuerySet[Section] = cast(Any, self).section_set

        for id, order, text in zip(section_ids, section_orders, sections):
            section: Section
            if id is None:
                section = section_set.create(
                    order=order,
                    text=text,
                    parent=self,
                )

                Role.objects.create(
                    user=user,
                    type=Role.Type.EDITOR,
                    target=section.role_target,
                )
                id = cast(Any, section).id
                present_ids.add(id)
            else:
                section = get_object_or_404(Section, id=id)
                if section.role_target.user_can_edit(user):
                    section.text = text
                    section.order = order
                    section.save()

        # Delete removed sections, if the user can delete them.
        for section in section_set.exclude(id__in=present_ids):
            if section.role_target.user_can_edit(user):
                section.delete()

class Section(RoleTargetBase, models.Model):
    """Represents a part of a Wiki article"""

    article = models.ForeignKey(
        Article,
        blank=False,
        null=False,
        on_delete=models.CASCADE
    )
    text = models.TextField(blank=False, null=False, help_text='Markdown text')

    # Order is in a range from 0 to the number of sections on the article.
    # Clients might not be able to see all the sections, but can still do
    # alright at preventing totally mangling an article as they edit it.
    order = models.FloatField(help_text="Section order in its article.", blank=False, null=False, default=0.0)

    def __str__(self):
        return self.text

    def __repr__(self):
        return f'<Section: {repr(self.text)}>'

    class Meta(RoleTargetBase.Meta):
        indexes = [
            models.Index(fields=('article', 'order'))
        ]

class ArticleBase(models.Model):
    '''An abstract base that gives an article field to a model.
    '''

    article = models.ForeignKey(
        Article,
        null=False,
        blank=False,
        on_delete=models.RESTRICT,
        related_name='+',
    )

    class Meta:
        abstract = True
