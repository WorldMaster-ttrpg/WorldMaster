#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2022 Taylor C. Richberger
# This code is released under the license described in the LICENSE file

from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'worlds'
urlpatterns = [
    path('', views.WorldsView.as_view(), name='worlds'),
    path('wm-new/', views.NewWorldView.as_view(), name='new-world'),
    path('<slug:world_slug>/', views.WorldView.as_view(), name='world'),
    path('<slug:world_slug>/edit/', views.EditWorldView.as_view(), name='edit-world'),
    path('<slug:world_slug>/planes/', views.PlanesView.as_view(), name='planes'),
    path('<slug:world_slug>/planes/wm-new/', views.NewPlaneView.as_view(), name='new-plane'),
    path('<slug:world_slug>/planes/<slug:plane_slug>/', views.PlaneView.as_view(), name='plane'),
    path('<slug:world_slug>/planes/<slug:plane_slug>/edit', views.EditPlaneView.as_view(), name='edit-plane'),
]
