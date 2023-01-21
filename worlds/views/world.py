from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView, ListView, DetailView, View
from django.views.decorators.http import require_http_methods
from worlds.models import World
from worlds.forms import WorldForm
from copy import copy

class WorldsView(ListView):
    model = World
    template_name = 'worlds/world/index.html'

class WorldView(DetailView):
    model = World
    slug_url_kwarg = 'world_slug'

    template_name = 'worlds/world/detail.html'

class NewWorldView(View):
    template_name = 'worlds/world/new.html'
    def get(self, request: HttpRequest) -> HttpResponse:
        form = WorldForm()
        return HttpResponse(render(request, self.template_name, {'form': form}))

    def post(self, request: HttpRequest) -> HttpResponse:
        form = WorldForm(request.POST)
        if form.is_valid():
            world: World = form.save()
            return redirect(world)
        else:
            return HttpResponseBadRequest(render(request, self.template_name, {'form': form}))

class EditWorldView(View):
    template_name = 'worlds/world/edit.html'
    def get(self, request: HttpRequest, world_slug: str) -> HttpResponse:
        world: World = get_object_or_404(World, slug=world_slug)
        form = WorldForm(instance=world)
        return HttpResponse(render(request, self.template_name, {'form': form, 'world': world}))

    def post(self, request: HttpRequest, world_slug: str) -> HttpResponse:
        world: World = get_object_or_404(World, slug=world_slug)

        # Copy the object in so that the bad request page doesn't get the
        # modified instance. If you don't do this and you try to change the
        # slug, even if it fails, the form action will be changed to match
        # the attempt.
        form = WorldForm(request.POST, instance=copy(world))
        if form.is_valid():
            return redirect(form.save())
        else:
            return HttpResponseBadRequest(render(request, self.template_name, {'form': form, 'world': world}))
