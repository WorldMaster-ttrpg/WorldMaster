from django.urls improt path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
