from django.shortcuts import render, get_object_or_404
from django.http import Http404
from wiki.models import Tag, AgeGroup, Game
from wiki.services import get_game_by_slug

def game_list(request):
    context = {
        'tags': Tag.get_all_tags(),
        'age_groups': AgeGroup.get_all_age_groups(),
    }

    return render(request, 'wiki/game_list.html', context)

def game_detail(request, slug):
    game = get_game_by_slug(slug)
    if not game:
        raise Http404(f"Game with slug '{slug}' not found")
    
    context = {
        'game': game,
    }
    
    return render(request, 'wiki/game_detail.html', context)
