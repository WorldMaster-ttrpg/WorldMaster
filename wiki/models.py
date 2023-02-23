from django.db import models
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
User = get_user_model()

class Article(models.Model):
    """Represents a Wiki article.

    These are wholly-owned objects. An article doesn't stand on its own, it
    is always part of something else.  It is mostly a convenience to group
    templates and permissions, so the parent object doesn't need to worry about
    it.
    """

class Section(models.Model):
    """Represents a part of a Wiki article"""

    article = models.ForeignKey(Article, blank=False, null=False, on_delete=models.CASCADE)
    text = models.TextField(blank=False, null=False, help_text='Markdown text')

    # Order is ranged 0 to 1, so articles can be edited by people who can't see
    # all the sections without completely destroying the order.
    order = models.FloatField(help_text="Order, in range [0, 1]", blank=False, null=False, default=0.0)

    def __str__(self):
        return self.text

def join_deletions(*deletions: tuple[int, dict[str, int]]) -> tuple[int, dict[str, int]]:
    '''Help join deletion return values for overriding a deletion method.

    Model.delete returns the count of rows deleted, and the objects deleted per
    type.  If you delete multiple things, it makes sense to merge these values.
    '''

    count = 0
    per_type: dict[str, int] = {}
    for i_count, i_per_type in deletions:
        count += i_count
        for type, c in i_per_type.items():
            per_type.setdefault(type, 0)
            per_type[type] += c
    return count, per_type

class ArticleBase(models.Model):
    '''Mark the model as a wiki article.

    Automatically deletes the wiki article on deletion via a signal.
    '''
    article = models.OneToOneField(
        Article,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
    )

    class Meta:
        abstract = True

