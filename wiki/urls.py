from django.urls import path

from . import views

app_name = 'wiki'

urlpatterns = [
    path("", views.home, name="home"),
    path("games/", views.GameListView.as_view(), name="game_list"),
    path("games/<slug:slug>/", views.GameDetailView.as_view(), name="game_detail"),
    path("games/<slug:slug>/rate/", views.rate_game, name="rate_game"),
    path("games/<slug:slug>/variant/", views.add_variant, name="add_variant"),
    path("games/<slug:slug>/edit/", views.GameUpdateView.as_view(), name="edit_game"),
    path("games/<slug:slug>/images/", views.upload_game_images, name="upload_game_images"),
    path("images/<int:pk>/delete/", views.delete_game_image, name="delete_game_image"),
    path("new-game/", views.GameCreateView.as_view(), name="new_game"),
]