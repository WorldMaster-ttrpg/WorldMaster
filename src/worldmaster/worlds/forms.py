from django import forms
from worldmaster.worlds.models import World, Plane
from django.template.defaultfilters import slugify

class SluggedForm(forms.ModelForm):
    class Meta:
        # Even though slug is a computed field, we want to run validation on
        # it.  The easiest way of doing that is keeping it as a useless hidden
        # field.  Without this, validation needs to be done manually and
        # doesn't reflect well in the form itself.
        fields = ['name', 'slug']

    # To allow new forms to not barf on validation before field can be cleaned.
    slug = forms.SlugField(required=False, widget=forms.HiddenInput())

    def clean_slug(self):
        return slugify(self.cleaned_data['name'])

class WorldForm(SluggedForm):
    class Meta(SluggedForm.Meta):
        model = World

class PlaneForm(SluggedForm):
    class Meta(SluggedForm.Meta):
        model = Plane
