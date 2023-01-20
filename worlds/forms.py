from django.forms import ModelForm
from worlds.models import World, Plane

class WorldForm(ModelForm):
    class Meta:
        model = World
        fields = ['name', 'slug', 'description']

class PlaneForm(ModelForm):
    class Meta:
        model = Plane
        fields = ['name', 'slug', 'description']
