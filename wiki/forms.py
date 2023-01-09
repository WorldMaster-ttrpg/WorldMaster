from django import forms
from .models import Article, EditArticle

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['author', 'slug']

class EditForm(forms.ModelForm):
    class Meta:
        model = EditArticle
        fields = ['summary']
