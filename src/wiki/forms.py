from django import forms
from .models import Article, Section

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title']

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['summary']
