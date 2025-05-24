from django.shortcuts import render
from wiki.models import Tag, AgeGroup

def game_list(request):
    context = {
        'tags': Tag.get_all_tags(),
        'age_groups': AgeGroup.get_all_age_groups(),
    }

    return render(request, 'wiki/game_list.html', context)
