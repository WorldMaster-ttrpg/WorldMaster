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
    path('new-world', views.NewWorldView.as_view(), name='new-world'),
    path('world/<slug:slug>/', views.WorldView.as_view(), name='world'),
    path('world/<slug:slug>/edit', views.EditWorldView.as_view(), name='edit-world'),
]
