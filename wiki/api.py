# MassiveGameArchive/wiki/api.py
from typing_extensions import Optional
from django.http import HttpRequest
from ninja import NinjaAPI, Schema, Query
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

@api.get(
    "/games",
    response={200: List[GameSchema], 400: ErrorResponseSchema},
    summary="Get a list of games",
    description="Returns a paginated list of games with optional filtering options."
)
def list_games(
    request: HttpRequest,
    start_index: int = Query(0, description="Starting index for pagination (0-based)"),
    amount: int = Query(20, description="Number of games to return per page (max 50)"),
    tag_filter: List[str] = Query([], description="List of tags to filter games by"),
    age_group_filter: List[str] = Query([], description="List of age groups to filter games by"),
    min_difficulty_index: int = Query(0, description="Minimum difficulty level (1-10)"),
    max_difficulty_index: int = Query(10, description="Maximum difficulty level (1-10)"),
    min_group_size_index: int = Query(0, description="Minimum group size level (1-10)"),
    max_group_size_index: int = Query(10, description="Maximum group size level (1-10)"),
    min_preperation_index: int = Query(0, description="Minimum preparation level (1-10)"),
    max_preperation_index: int = Query(10, description="Maximum preparation level (1-10)"),
    min_physical_index: int = Query(0, description="Minimum physical activity level (1-10)"),
    max_physical_index: int = Query(10, description="Maximum physical activity level (1-10)"),
    min_duration_index: int = Query(0, description="Minimum game duration level (1-10)"),
    max_duration_index: int = Query(10, description="Maximum game duration level (1-10)"),
):
    start_index = int(start_index)
    amount = int(amount)

    if amount > 50:
        return JsonResponse(
            ErrorResponseSchema(error="Amount exceeds maximum limit of 50 games per request"),
            status=400
        )

    games_queryset = Game.objects.all()

    if tag_filter:
        for tag in tag_filter:
            games_queryset = games_queryset.filter(tags__name=tag)

    if age_group_filter:
        for age_group in age_group_filter:
            games_queryset = games_queryset.filter(age_groups__name=age_group)

    games_queryset = games_queryset.filter(
        difficulty_index__gte=min_difficulty_index,
        difficulty_index__lte=max_difficulty_index,
        group_size_index__gte=min_group_size_index,
        group_size_index__lte=max_group_size_index,
        preperation_index__gte=min_preperation_index,
        preperation_index__lte=max_preperation_index,
        physical_index__gte=min_physical_index,
        physical_index__lte=max_physical_index,
        duration_index__gte=min_duration_index,
        duration_index__lte=max_duration_index,
    )

    end_index = start_index + amount
    games = games_queryset[start_index:end_index]

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
