from django.db import models
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
User = get_user_model()

class PublishedArticlesManager(models.Manager):
    """Queryset that returns only published articles"""
    def get_query_set(self):
        return super(PublishedArticlesManager, self).get_query_set().filter(is_published=True)

class Article(models.Model):
    """Represents a Wiki article"""

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, unique=True)
    text = models.TextField(help_text="Formatted using ReST")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False, verbose_name="Publish?")
    objects = models.Manager()
    published = PublishedArticlesManager()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)

class EditArticle(models.Model):
    """Stores an edit session of an article"""

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    editor = models.ForeignKey(User, on_delete=models.CASCADE)
    edited_on = models.DateTimeField(auto_now_add=True)
    summary = models.CharField(max_length=100)
    objects = models.Manager()

    class Meta:
        ordering = ['-edited_on']

    def __unicode__(self):
        return "%s - %s - %s" % (self.summary, self.editor, self.edited_on)
