from __future__ import annotations
from typing import cast
from django.core.exceptions import PermissionDenied

from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from roles.models import Role
from worlds.models import World, Plane
from worlds.forms import PlaneForm
from copy import copy
from worldmaster import models as worldmaster

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

class NewPlaneView(LoginRequiredMixin, View):
    template_name = 'worlds/plane/new.html'

    def get(self, request: HttpRequest, world_slug: str) -> HttpResponse:
        with transaction.atomic():
            world = get_object_or_404(World, slug=world_slug)
            user = cast(worldmaster.User, request.user)
            if not world.role_target.user_can_edit(user):
                raise PermissionDenied('User can not edit world')
            form = PlaneForm(world=world)
            context = {
                'form': form,
                'world': world,
            }
            return HttpResponse(render(request, self.template_name, context))

    def post(self, request: HttpRequest, world_slug: str) -> HttpResponse:
        with transaction.atomic():
            world = get_object_or_404(World, slug=world_slug)
            user = cast(worldmaster.User, request.user)
            if not world.role_target.user_can_edit(user):
                raise PermissionDenied('User can not edit world')
            form = PlaneForm(request.POST, world=world)
            if form.is_valid():
                form.instance.world = world
                plane: Plane = form.save()
                user = cast(worldmaster.User, request.user)
                Role.objects.create(
                    user=request.user,
                    type=Role.Type.EDITOR,
                    target=plane.role_target,
                )
                return redirect(plane)
            else:
                return HttpResponseBadRequest(render(request, self.template_name, {'form': form, 'world': world}))

class EditPlaneView(LoginRequiredMixin, View):
    template_name = 'worlds/plane/edit.html'

    def get(self, request: HttpRequest, world_slug: str, plane_slug: str) -> HttpResponse:
        with transaction.atomic():
            plane: Plane = get_object_or_404(Plane, world__slug=world_slug, slug=plane_slug)
            user = cast(worldmaster.User, request.user)
            if not plane.role_target.user_can_edit(user):
                raise PermissionDenied('User can not edit plane')
            form = PlaneForm(instance=plane)
            return HttpResponse(render(request, self.template_name, {'form': form, 'object': plane}))

    def post(self, request: HttpRequest, world_slug: str, plane_slug: str) -> HttpResponse:
        with transaction.atomic():
            plane: Plane = get_object_or_404(Plane, world__slug=world_slug, slug=plane_slug)
            user = cast(worldmaster.User, request.user)
            if not plane.role_target.user_can_edit(user):
                raise PermissionDenied('User can not edit plane')

            # Copy the object in so that the bad request page doesn't get the
            # modified instance. If you don't do this and you try to change the
            # slug, even if it fails, the form action will be changed to match
            # the attempt.
            # We might want to counteract this by just making the slug non-
            # editable. This would also avoid breaking links.
            form = PlaneForm(request.POST, instance=copy(plane))
            if form.is_valid():
                plane.article.update_sections(
                    user=user,
                    data=request.POST,
                )

                return redirect(form.save())
            else:
                return HttpResponseBadRequest(render(request, self.template_name, {'form': form, 'object': plane}))
