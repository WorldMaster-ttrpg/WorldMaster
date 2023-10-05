"""worldmaster URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/

Examples
--------
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
from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import include, path, reverse


def redirect_to_worlds(request: HttpRequest) -> HttpResponse:
    """Redirect to worlds."""
    return HttpResponseRedirect(reverse("worlds:worlds"))

app_name = "worldmaster"

urlpatterns = (
    path("", redirect_to_worlds),
    path("admin/", admin.site.urls),
    path("worlds/", include("worldmaster.worlds.urls")),
    path("accounts/", include(("django.contrib.auth.urls", "auth"))),
)

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns = (
        *urlpatterns,
        *staticfiles_urlpatterns(),
    )


