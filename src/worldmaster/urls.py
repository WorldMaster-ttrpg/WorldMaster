"""worldmaster URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

# Convenience redirect to worlds
def redirect_to_worlds(request: HttpRequest) -> HttpResponse:
    return HttpResponseRedirect(reverse('worlds:worlds'))

urlpatterns = [
    path('', redirect_to_worlds),
    path('admin/', admin.site.urls),
    #path('wiki/', include('wiki.urls')),
    path('worlds/', include('worlds.urls', namespace='worlds')),
]
