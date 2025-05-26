from django.urls import path

from . import views
from wiki.api import api

urlpatterns = [
    path("", views.game_list, name="game_list"),
    path("game/<slug:slug>/", views.game_detail, name="game_detail"),
    path("api/v1/", api.urls)
]
