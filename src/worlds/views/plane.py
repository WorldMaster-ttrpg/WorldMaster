from __future__ import annotations
from typing import Any, cast
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.core.exceptions import PermissionDenied

from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from roles.models import Role
from worlds.models import World, Plane
from worlds.forms import PlaneForm
from copy import copy
from worldmaster import models as worldmaster

class PlanesView(ListView):
    model = Plane
    template_name = 'worlds/plane/index.html'

    def setup(self, request, *args, world_slug, **kwargs) -> None:
        super().setup(request, *args, world_slug=world_slug, **kwargs)
        self.__world = World.objects.visible_to(
            cast(AbstractUser | AnonymousUser, self.request.user)
        ).filter(slug=world_slug).get()

    def get_queryset(self):
        '''Get planes in this world visible to this user.
        '''
        return Plane.objects.visible_to(
            cast(AbstractUser | AnonymousUser, self.request.user)
        ).filter(world=self.__world)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['world'] = self.__world
        return context

class PlaneView(DetailView):
    model = Plane
    template_name = 'worlds/plane/detail.html'
    slug_url_kwarg = 'plane_slug'

    def setup(self, request, *args, world_slug, **kwargs) -> None:
        super().setup(request, *args, world_slug=world_slug, **kwargs)
        self.__world = World.objects.visible_to(
            cast(AbstractUser | AnonymousUser, self.request.user)
        ).filter(slug=world_slug).get()

    def get_queryset(self):
        '''Get planes in this world visible to this user.
        '''
        return Plane.objects.visible_to(
            cast(AbstractUser | AnonymousUser, self.request.user)
        ).filter(world=self.__world)

class NewPlaneView(LoginRequiredMixin, CreateView):
    model = Plane
    form_class = PlaneForm
    template_name = 'worlds/plane/new.html'

    object: Plane

    def get_form(self, form_class=None) -> PlaneForm:
        form: PlaneForm = super().get_form(form_class)
        form.instance.world = World.objects.editable_by(
            cast(AbstractUser | AnonymousUser, self.request.user)
        ).filter(slug=self.kwargs['world_slug']).get()

        return form

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data['action'] = reverse('worlds:new-plane', kwargs={
            'world_slug': self.kwargs['world_slug'],
        })
        return data

    def form_valid(self, form: PlaneForm) -> HttpResponse:
        response = super().form_valid(form)
        kwargs = {
            'user': self.request.user,
            'type': Role.Type.EDITOR,
            'target': self.object.role_target,
        }
        if not Role.objects.filter(**kwargs).exists():
            Role.objects.create(**kwargs)
        return response

    @transaction.atomic
    def post(self, *args, **kwargs) -> HttpResponse:
        return super().post(*args, **kwargs)

class EditPlaneView(LoginRequiredMixin, UpdateView):
    template_name = 'worlds/plane/edit.html'
    model = Plane
    slug_url_kwarg = 'plane_slug'
    form_class = PlaneForm
    template_name = 'worlds/plane/edit.html'
    object: Plane

    def get_queryset(self):
        '''Get planes in this world visible to this user.
        '''
        return Plane.objects.visible_to(
            cast(AbstractUser | AnonymousUser, self.request.user)
        ).filter(world__slug=self.kwargs['world_slug'])

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data['action'] = reverse('worlds:edit-plane', kwargs={
            'world_slug': self.kwargs['world_slug'],
            'plane_slug': self.kwargs['plane_slug'],
        })
        return data

    @transaction.atomic
    def post(self, *args, **kwargs) -> HttpResponse:
        return super().post(*args, **kwargs)

    def form_valid(self, form: PlaneForm) -> HttpResponse:
        response = super().form_valid(form)
        self.object.article.update_sections(
            user=self.request.user,
            data=self.request.POST,
        )
        return response
