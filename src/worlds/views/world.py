from typing import cast
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, View
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from worlds.models import World
from worlds.forms import WorldForm
from roles.models import Role
from copy import copy

User = cast(type[AbstractUser], get_user_model())

class WorldsView(ListView):
    model = World
    template_name = 'worlds/world/index.html'

    def get_queryset(self) -> QuerySet[World]:
        '''Get the visible worlds for the given user.
        '''
        return World.visible_to(cast(AbstractUser | AnonymousUser, self.request.user))

class WorldView(DetailView):
    model = World
    slug_url_kwarg = 'world_slug'
    template_name = 'worlds/world/detail.html'

    def get_queryset(self) -> QuerySet[World]:
        '''Get the visible worlds for the given user.
        '''
        return World.visible_to(cast(AbstractUser | AnonymousUser, self.request.user))

class NewWorldView(LoginRequiredMixin, View):
    template_name = 'worlds/world/new.html'
    def get(self, request: HttpRequest) -> HttpResponse:
        form = WorldForm()
        return HttpResponse(render(request, self.template_name, {'form': form}))

    def post(self, request: HttpRequest) -> HttpResponse:
        with transaction.atomic():
            form = WorldForm(request.POST)
            if form.is_valid():
                world: World = form.save()
                Role.objects.create(
                    user=request.user,
                    type=Role.Type.MASTER,
                    target=world.role_target,
                )
                return redirect(world)
            else:
                return HttpResponseBadRequest(render(request, self.template_name, {'form': form}))

class EditWorldView(LoginRequiredMixin, View):
    template_name = 'worlds/world/edit.html'
    def get(self, request: HttpRequest, world_slug: str) -> HttpResponse:
        user = cast(AbstractUser | AnonymousUser, request.user)
        world: World = get_object_or_404(World, slug=world_slug)
        if not world.role_target.user_is_editor(user):
            raise PermissionDenied('User can not edit world')
        form = WorldForm(instance=world)
        return HttpResponse(render(request, self.template_name, {'form': form, 'object': world}))

    def post(self, request: HttpRequest, world_slug: str) -> HttpResponse:
        with transaction.atomic():
            user = cast(AbstractUser | AnonymousUser, request.user)
            world: World = get_object_or_404(World, slug=world_slug)
            if not world.role_target.user_is_editor(user):
                raise PermissionDenied('User can not edit world')

            # Copy the object in so that the bad request page doesn't get the
            # modified instance. If you don't do this and you try to change the
            # slug, even if it fails, the form action will be changed to match
            # the attempt.
            form = WorldForm(request.POST, instance=copy(world))
            if form.is_valid():
                world = cast(World, form.save())
                world.article.update_sections(
                    user=user,
                    data=request.POST,
                )

                players = frozenset(request.POST.getlist('player', ()))
                old_players: frozenset[str] = frozenset(world.players.all().values_list('username', flat=True))
                added_players = players - old_players
                removed_players = old_players - players

                for username in removed_players:
                    world.players.remove(User.objects.get(username=username))

                for username in added_players:
                    world.players.add(User.objects.get(username=username))

                return redirect(form.save())
            else:
                return HttpResponseBadRequest(render(request, self.template_name, {'form': form, 'object': world}))
