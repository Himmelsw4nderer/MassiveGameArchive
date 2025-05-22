# MassiveGameArchive/wiki/api.py
from django.http import HttpRequest
from ninja import NinjaAPI, Schema
from typing import List
from .models import Game
from django.http import JsonResponse


api = NinjaAPI(urls_namespace="wiki_api")

class GameSchema(Schema):
    id: int
    title: str
    short_description: str
    slug: str


class ErrorResponseSchema(Schema):
    error: str


@api.get("/games", response={200: List[GameSchema], 400: ErrorResponseSchema}, summary="Get a list of games", description="Returns a paginated list of games. Start index and amount must be specified.")
def list_games(request: HttpRequest, start_index: int = 0, amount: int = 20):
    start_index = int(start_index)
    amount = int(amount)

    if amount > 50:
        return JsonResponse(
            ErrorResponseSchema("Amount exceeds maximum limit of 50 games per request"),
            status=400
        )

    end_index = start_index + amount
    games = Game.objects.all()[start_index:end_index]
    return [
        GameSchema(
            id=game.id,
            title=game.title,
            short_description=game.short_description,
            slug=game.slug
        ) for game in games
    ]
