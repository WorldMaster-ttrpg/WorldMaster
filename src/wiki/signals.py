from typing import Any
from django.dispatch import receiver
from django.db.models.signals import post_delete
from .models import ArticleBase

# This needs to happen in a signal, because overriding delete() does not work
# for bulk deletion.
@receiver(post_delete)
def delete_child_article(sender: Any, instance: Any, **kwargs):
    if isinstance(instance, ArticleBase):
        instance.article.delete()
