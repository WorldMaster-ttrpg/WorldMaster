from typing import Any, cast
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView, ListView, DetailView, View
from django.views.decorators.http import require_http_methods
from worlds.models import World, Plane
from worlds.forms import PlaneForm

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['world'] = self.__world
        return context

class NewPlaneView(View):
    template_name = 'worlds/plane/new.html'

    def get(self, request: HttpRequest, world_slug: str) -> HttpResponse:
        form = PlaneForm()
        context = {
            'form': form,
            'world': get_object_or_404(World, slug=world_slug),
        }
        return HttpResponse(render(request, self.template_name, context))

    def post(self, request: HttpRequest, world_slug: str) -> HttpResponse:
        world = get_object_or_404(World, slug=world_slug)
        form = PlaneForm(request.POST)
        if form.is_valid():
            plane: Plane = form.save(commit=False)
            plane.world = world
            plane.save()
            return redirect(plane)
        else:
            return HttpResponseBadRequest(render(request, self.template_name, {'form': form}))

class EditPlaneView(View):
    template_name = 'worlds/plane/edit.html'
    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        plane: Plane = get_object_or_404(Plane, slug=slug)
        form = PlaneForm(instance=plane)
        return HttpResponse(render(request, self.template_name, {'form': form, 'plane': plane}))

    def post(self, request: HttpRequest, slug: str) -> HttpResponse:
        plane: Plane = get_object_or_404(Plane, slug=slug)
        form = PlaneForm(request.POST, instance=plane)
        if form.is_valid():
            plane: Plane = form.save()
            return redirect(plane)
        else:
            return HttpResponseBadRequest(render(request, self.template_name, {'form': form}))
