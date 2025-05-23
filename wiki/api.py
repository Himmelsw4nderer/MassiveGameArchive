# MassiveGameArchive/wiki/api.py
from django.http import HttpRequest
from ninja import NinjaAPI, Schema
from typing import List
from .models import Game
from django.http import JsonResponse


api = NinjaAPI(urls_namespace="wiki_api")
class GameSchema(Schema):
    title: str
    short_description: str
    slug: str
    difficulty_index: int
    group_size_index: int
    preperation_index: int
    physical_index: int
    duration_index: int
    tags: List[str]
    age_groups: List[str]
    upvote_count: int
    downvote_count: int


class ErrorResponseSchema(Schema):
    error: str


@api.get("/games", response={200: List[GameSchema], 400: ErrorResponseSchema}, summary="Get a list of games", description="Returns a paginated list of games. Start index and amount must be specified.")
def list_games(request: HttpRequest, start_index: int = 0, amount: int = 20):
    start_index = int(start_index)
    amount = int(amount)

    if amount > 50:
        return JsonResponse(
            ErrorResponseSchema(error="Amount exceeds maximum limit of 50 games per request"),
            status=400
        )

    end_index = start_index + amount
    games = Game.objects.all()[start_index:end_index]
    return [
        GameSchema(
            title=game.title,
            short_description=game.short_description,
            slug=game.slug,
            difficulty_index=game.difficulty_index,
            group_size_index=game.group_size_index,
            preperation_index=game.preperation_index,
            physical_index=game.physical_index,
            duration_index=game.duration_index,
            tags=game.get_tags(),
            age_groups=game.get_age_groups(),
            upvote_count=game.get_upvote_count(),
            downvote_count=game.get_downvote_count(),
        ) for game in games
    ]
