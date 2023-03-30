from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView, ListView, DetailView, View
from django.views.decorators.http import require_http_methods
from django.db import transaction
from wiki.models import Article, Section
from worlds.models import World
from worlds.forms import WorldForm
from copy import copy
import json

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
        form.instance.article = Article.objects.create()
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
        with transaction.atomic():
            world: World = get_object_or_404(World, slug=world_slug)

            # Copy the object in so that the bad request page doesn't get the
            # modified instance. If you don't do this and you try to change the
            # slug, even if it fails, the form action will be changed to match
            # the attempt.
            form = WorldForm(request.POST, instance=copy(world))
            if form.is_valid():
                instance = form.save()
                # Now save the wiki.
                # TODO: Move this somewhere reusable, like in the Article model,
                # or even an Article view.  Perhaps a sub-view thing, maybe with
                # a sub-form object for better composeability.
                article: Article = world.article

                # Not a set or dict because None may appear multiple times
                print(request.POST)

                def load_int(value: str) -> int | None:
                    '''Load an integer if the string is not empty, otherwise None.
                    '''
                    if value:
                        return int(value)
                    else:
                        return None

                section_ids = tuple(map(load_int, request.POST.getlist('wiki-section-id')))

                section_orders = map(float, request.POST.getlist('wiki-section-order'))
                sections = request.POST.getlist('wiki-section')

                present_ids = set(id for id in section_ids if id is not None)

                for id, order, text in zip(section_ids, section_orders, sections):
                    if id is None:
                        section = article.section_set.create(order=order, text=text)
                        present_ids.add(section.id)
                    else:
                        section: Section = get_object_or_404(Section, id=id)
                        section.text = text
                        section.order = order
                        section.save()

                # Delete removed sections
                article.section_set.exclude(id__in=present_ids).delete()
                return redirect(instance)
            else:
                return HttpResponseBadRequest(render(request, self.template_name, {'form': form, 'world': world}))
