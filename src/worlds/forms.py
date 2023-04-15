from django import forms
from django.contrib.auth.models import AbstractBaseUser
from worlds.models import World, Plane
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

    def __init__(self, *args, master: AbstractBaseUser | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if master is not None:
            self.instance.master = master

        if self.instance.master is None:
            raise ValueError('World needs a master')

class PlaneForm(SluggedForm):
    class Meta(SluggedForm.Meta):
        model = Plane

    def __init__(self, *args, world: World | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if world is not None:
            self.instance.world = world

        if self.instance.world is None:
            raise ValueError('PlaneForm needs a world')

    def clean_slug(self):
        return slugify(self.cleaned_data['name'])
