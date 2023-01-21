from django import forms
from worlds.models import World, Plane
from django.template.defaultfilters import slugify
from django.utils.translation import gettext as _

class WorldForm(forms.ModelForm):
    class Meta:
        model = World
        # Even though slug is a computed field, we want to run validation on
        # it.  The easiest way of doing that is keeping it as a useless hidden
        # field.  Without this, validation needs to be done manually and
        # doesn't reflect well in the form itself.
        fields = ['name', 'slug']

    # To allow new forms to not barf on validation before field can be cleaned.
    slug = forms.SlugField(required=False, widget=forms.HiddenInput())

    def clean_slug(self):
        return slugify(self.cleaned_data['name'])

class PlaneForm(forms.ModelForm):
    class Meta:
        model = Plane
        fields = ['name', 'slug']
        widgets = {'slug': forms.HiddenInput()}

    # To allow new forms to not barf on validation before field can be cleaned.
    slug = forms.SlugField(required=False)

    def __init__(self, *args, world: World | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if world is not None:
            self.instance.world = world

        assert self.instance.world is not None

    def clean_slug(self):
        return slugify(self.cleaned_data['name'])
