from django.shortcuts import render

def game_list(request):
    return render(request, 'wiki/game_list.html')
