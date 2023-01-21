from django.db import models
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
User = get_user_model()

class Article(models.Model):
    """Represents a Wiki article"""

    title = models.CharField(blank=False, null=False, max_length=256)
    slug = models.SlugField(blank=False, null=False, max_length=50, unique=True)

    def __str__(self):
        return self.title

class Section(models.Model):
    """Represents a part of a Wiki article"""

    article = models.ForeignKey(Article, blank=False, null=False, on_delete=models.CASCADE)
    text = models.TextField(blank=False, null=False, help_text='Markdown text')

    # Order is ranged 0 to 1, so articles can be edited by people who can't see all the notes without completely destroying the order. 
    order = models.FloatField(help_text="Order, in range [0, 1]", blank=False, null=False, default=0.0)

    def __str__(self):
        return self.text
