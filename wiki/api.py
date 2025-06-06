# MassiveGameArchive/wiki/api.py
"""
API endpoints for the Wiki app.

This module provides the API endpoints for the Wiki app, including:
- Game listing with advanced search and filtering capabilities
- Customizable search fields and sorting options

Search functionality:
- Use 'q' parameter for search queries (e.g., ?q=fun outdoor game)
- Control which fields to search with 'search_in' parameter (options: 'title', 'description', 'content', 'all')
- Sort results with 'sort_by' parameter (options: 'relevance', 'title', 'newest', 'upvotes')
- Advanced search is implemented in the services module for better code organization
"""

from django.http import HttpRequest, JsonResponse
from ninja import NinjaAPI, Schema, Query, Path
from typing import List, Optional
from .services import search_games, get_paginated_games, get_pagination_metadata, get_game_by_slug


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

class GameDetailSchema(GameSchema):
    markdown_content: Optional[str] = None
    creator_username: str
    created_at: str

class PaginationMetadataSchema(Schema):
    total_count: int
    total_pages: int

class GameListResponseSchema(Schema):
    games: List[GameSchema]
    pagination: PaginationMetadataSchema


class ErrorResponseSchema(Schema):
    error: str

class NotFoundResponseSchema(Schema):
    detail: str

@api.get(
    "/games",
    response={200: GameListResponseSchema, 400: ErrorResponseSchema},
    summary="Get a list of games",
    description="Returns a paginated list of games with optional filtering and search options along with pagination metadata."
)
def list_games(
    request: HttpRequest,
    start_index: int = Query(0, description="Starting index for pagination (0-based)"),
    amount: int = Query(20, description="Number of games to return per page (max 50)"),
    q: str = Query("", description="Search query for finding games by title, description, and content"),
    search_in: List[str] = Query(["all"], description="Fields to search in: 'title', 'description', 'content', or 'all'"),
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
    sort_by: str = Query("relevance", description="Sort results by: 'relevance', 'title', 'newest', 'upvotes'"),
):
    start_index = int(start_index)
    amount = int(amount)

    if amount > 50:
        return JsonResponse(
            ErrorResponseSchema(error="Amount exceeds maximum limit of 50 games per request"),
            status=400
        )

    games_queryset = search_games(
        query=q,
        search_in=search_in,
        tag_filter=tag_filter,
        age_group_filter=age_group_filter,
        min_difficulty_index=min_difficulty_index,
        max_difficulty_index=max_difficulty_index,
        min_group_size_index=min_group_size_index,
        max_group_size_index=max_group_size_index,
        min_preperation_index=min_preperation_index,
        max_preperation_index=max_preperation_index,
        min_physical_index=min_physical_index,
        max_physical_index=max_physical_index,
        min_duration_index=min_duration_index,
        max_duration_index=max_duration_index,
        sort_by=sort_by
    )

    games = get_paginated_games(games_queryset, start_index, amount)

    pagination_metadata = get_pagination_metadata(games_queryset, amount)

    return GameListResponseSchema(
        games=[
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
        ],
        pagination=PaginationMetadataSchema(
            total_count=pagination_metadata["total_count"],
            total_pages=pagination_metadata["total_pages"]
        )
    )

@api.get(
    "/games/{slug}",
    response={200: GameDetailSchema, 404: NotFoundResponseSchema},
    summary="Get game details by slug",
    description="Returns detailed information about a specific game identified by its slug."
)
def get_game_detail(
    request: HttpRequest,
    slug: str = Path(..., description="The unique slug identifier for the game"),
):
    game = get_game_by_slug(slug)

    if not game:
        return JsonResponse(
            NotFoundResponseSchema(detail=f"Game with slug '{slug}' not found"),
            status=404
        )

    return GameDetailSchema(
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
        markdown_content=game.markdown_content,
        creator_username=game.creator.username,
        created_at=game.created_at.isoformat(),
    )
