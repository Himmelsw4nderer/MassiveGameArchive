"""
Search utilities for the wiki app.

This module provides search functionalities for games in the wiki app,
separating the complex search logic from the API endpoints.
"""

from typing import List
from django.db.models import Q, Count, Case, When, IntegerField, QuerySet
from django.db import connection
from .models import Game

# For PostgreSQL full-text search
try:
    from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
    HAS_POSTGRES_SEARCH = True
except ImportError:
    HAS_POSTGRES_SEARCH = False

def search_games(
    query: str = "",
    search_in: List[str] = ["all"],
    tag_filter: List[str] = [],
    age_group_filter: List[str] = [],
    min_difficulty_index: int = 0,
    max_difficulty_index: int = 10,
    min_group_size_index: int = 0,
    max_group_size_index: int = 10,
    min_preperation_index: int = 0,
    max_preperation_index: int = 10,
    min_physical_index: int = 0,
    max_physical_index: int = 10,
    min_duration_index: int = 0,
    max_duration_index: int = 10,
    sort_by: str = "relevance",
) -> QuerySet:
    """
    Search and filter games based on various criteria.
    
    Args:
        query: Search query for finding games by title, description, and content
        search_in: Fields to search in: 'title', 'description', 'content', or 'all'
        tag_filter: List of tags to filter games by
        age_group_filter: List of age groups to filter games by
        min_difficulty_index: Minimum difficulty level (1-10)
        max_difficulty_index: Maximum difficulty level (1-10)
        min_group_size_index: Minimum group size level (1-10)
        max_group_size_index: Maximum group size level (1-10)
        min_preperation_index: Minimum preparation level (1-10)
        max_preperation_index: Maximum preparation level (1-10)
        min_physical_index: Minimum physical activity level (1-10)
        max_physical_index: Maximum physical activity level (1-10)
        min_duration_index: Minimum game duration level (1-10)
        max_duration_index: Maximum game duration level (1-10)
        sort_by: Sort results by: 'relevance', 'title', 'newest', 'upvotes'
    
    Returns:
        QuerySet of filtered and sorted Game objects
    """
    games_queryset = Game.objects.all()

    # Apply text search if query provided
    if query:
        games_queryset = _apply_text_search(games_queryset, query, search_in)

    # Apply tag filtering
    if tag_filter:
        for tag in tag_filter:
            games_queryset = games_queryset.filter(tags__name=tag)

    # Apply age group filtering
    if age_group_filter:
        for age_group in age_group_filter:
            games_queryset = games_queryset.filter(age_groups__name=age_group)

    # Apply range filtering
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

    # Apply sorting
    games_queryset = _apply_sorting(games_queryset, sort_by)

    return games_queryset

def _apply_text_search(queryset: QuerySet, query: str, search_in: List[str]) -> QuerySet:
    """Apply text search to the queryset."""
    if HAS_POSTGRES_SEARCH and connection.vendor == 'postgresql':
        search_vector = SearchVector('title', weight='A') + \
                       SearchVector('short_description', weight='B') + \
                       SearchVector('markdown_content', weight='C')
        search_query = SearchQuery(query)
        queryset = queryset.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank')
    else:
        search_query = Q()

        fields_to_search = []
        if "all" in search_in or not search_in:
            fields_to_search = ["title", "short_description", "markdown_content"]
        else:
            if "title" in search_in:
                fields_to_search.append("title")
            if "description" in search_in:
                fields_to_search.append("short_description")
            if "content" in search_in:
                fields_to_search.append("markdown_content")

        for term in query.split():
            term_query = Q()
            for field in fields_to_search:
                term_query |= Q(**{f"{field}__icontains": term})
            search_query &= term_query

        queryset = queryset.filter(search_query)
    
    return queryset

def _apply_sorting(queryset: QuerySet, sort_by: str) -> QuerySet:
    """Apply sorting to the queryset."""
    if sort_by == "title":
        queryset = queryset.order_by("title")
    elif sort_by == "newest":
        queryset = queryset.order_by("-created_at")
    elif sort_by == "upvotes":
        queryset = queryset.annotate(
            upvote_count=Count(
                Case(
                    When(votes__value=1, then=1),
                    output_field=IntegerField()
                )
            )
        ).order_by("-upvote_count")
    
    return queryset

def get_paginated_games(queryset: QuerySet, start_index: int, amount: int) -> List[Game]:
    """
    Get a paginated subset of games from a queryset.
    
    Args:
        queryset: QuerySet of Game objects
        start_index: Starting index for pagination (0-based)
        amount: Number of games to return
    
    Returns:
        List of Game objects
    """
    end_index = start_index + amount
    return list(queryset[start_index:end_index])