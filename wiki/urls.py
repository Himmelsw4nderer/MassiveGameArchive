from django.urls import path

from . import views
from wiki.api import api

urlpatterns = [
    path("", views.game_list, name="game_list"),
    path("api/v1/", api.urls)
]
