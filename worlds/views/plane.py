from typing import Any, cast
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView, ListView, DetailView, View
from django.views.decorators.http import require_http_methods
from worlds.models import World, Plane
from worlds.forms import PlaneForm
from copy import copy

class PlanesView(ListView):
    model = Plane
    template_name = 'worlds/plane/index.html'

    def setup(self, request, world_slug, *args, **kwargs):
        super().setup(request, world_slug, *args, **kwargs)
        self.__world = get_object_or_404(World, slug=world_slug)

    def get_queryset(self):
        return Plane.objects.filter(world=self.__world)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['world'] = self.__world
        return context

class PlaneView(DetailView):
    model = Plane
    template_name = 'worlds/plane/detail.html'
    slug_url_kwarg = 'plane_slug'

    def setup(self, request, world_slug, *args, **kwargs):
        super().setup(request, world_slug, *args, **kwargs)
        self.__world = get_object_or_404(World, slug=world_slug)

    def get_queryset(self):
        return Plane.objects.filter(world=self.__world)

class NewPlaneView(View):
    template_name = 'worlds/plane/new.html'

    def get(self, request: HttpRequest, world_slug: str) -> HttpResponse:
        world = get_object_or_404(World, slug=world_slug)
        form = PlaneForm(world=world)
        context = {
            'form': form,
            'world': world,
        }
        return HttpResponse(render(request, self.template_name, context))

    def post(self, request: HttpRequest, world_slug: str) -> HttpResponse:
        world = get_object_or_404(World, slug=world_slug)
        form = PlaneForm(request.POST, world=world)
        if form.is_valid():
            return redirect(form.save())
        else:
            return HttpResponseBadRequest(render(request, self.template_name, {'form': form, 'world': world}))

class EditPlaneView(View):
    template_name = 'worlds/plane/edit.html'
    def get(self, request: HttpRequest, world_slug: str, plane_slug: str) -> HttpResponse:
        plane: Plane = get_object_or_404(Plane, world__slug=world_slug, slug=plane_slug)
        form = PlaneForm(instance=plane)
        return HttpResponse(render(request, self.template_name, {'form': form, 'plane': plane}))

    def post(self, request: HttpRequest, world_slug: str, plane_slug: str) -> HttpResponse:
        plane: Plane = get_object_or_404(Plane, slug=plane_slug)
        # Copy the object in so that the bad request page doesn't get the
        # modified instance. If you don't do this and you try to change the
        # slug, even if it fails, the form action will be changed to match
        # the attempt.
        form = PlaneForm(request.POST, instance=copy(plane))
        if form.is_valid():
            return redirect(form.save())
        else:
            return HttpResponseBadRequest(render(request, self.template_name, {'form': form, 'plane': plane}))
