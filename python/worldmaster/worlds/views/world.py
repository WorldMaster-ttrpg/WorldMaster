from typing import Any, cast

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from worldmaster.roles.models import Role
from worldmaster.worlds.forms import WorldForm
from worldmaster.worlds.models import World

User = cast(type[AbstractUser], get_user_model())

class WorldsView(ListView):
    model = World
    template_name = "worlds/world/index.html"

    def get_queryset(self) -> QuerySet[World]:
        """Get the visible worlds for the given user."""
        return World.objects.visible_to(cast(AbstractUser | AnonymousUser, self.request.user))

class WorldView(DetailView):
    model = World
    slug_url_kwarg = "world_slug"
    template_name = "worlds/world/detail.html"

    def get_queryset(self) -> QuerySet[World]:
        """Get the visible worlds for the given user."""
        return World.objects.visible_to(cast(AbstractUser | AnonymousUser, self.request.user))

class NewWorldView(LoginRequiredMixin, CreateView):
    model = World
    form_class = WorldForm
    template_name = "worlds/world/new.html"
    object: World

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data["action"] = reverse("worlds:new-world")
        return data

    def form_valid(self, form: WorldForm) -> HttpResponse:
        response = super().form_valid(form)
        Role.objects.create(
            user=self.request.user,
            type=Role.Type.MASTER,
            target=self.object.role_target,
        )
        return response

    @transaction.atomic
    def post(self, *args, **kwargs) -> HttpResponse:
        return super().post(*args, **kwargs)

class EditWorldView(LoginRequiredMixin, UpdateView):
    model = World
    slug_url_kwarg = "world_slug"
    form_class = WorldForm
    template_name = "worlds/world/edit.html"
    object: World

    def get_queryset(self) -> QuerySet[World]:
        """Get the visible worlds for the given user."""
        return World.objects.visible_to(cast(AbstractUser | AnonymousUser, self.request.user))

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        # Not self.object.slug so we don't mangle the action on a failed update.
        data["action"] = reverse("worlds:edit-world", kwargs={"world_slug": self.kwargs["world_slug"]})
        return data

    @transaction.atomic
    def post(self, *args, **kwargs) -> HttpResponse:
        return super().post(*args, **kwargs)

    def form_valid(self, form: WorldForm) -> HttpResponse:
        response = super().form_valid(form)

        self.object.article.update_sections(
            user=self.request.user,
            data=self.request.POST,
        )

        players = frozenset(self.request.POST.getlist("player", ()))
        old_players: frozenset[str] = frozenset(self.object.players.all().values_list("username", flat=True))
        added_players = players - old_players
        removed_players = old_players - players

        for username in removed_players:
            self.object.players.remove(User.objects.get(username=username))

        for username in added_players:
            self.object.players.add(User.objects.get(username=username))

        return response
