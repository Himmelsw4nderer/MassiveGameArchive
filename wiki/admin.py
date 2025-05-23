from django.contrib import admin
from wiki.models import Game, Tag, AgeGroup, Vote

admin.site.register(Game)
admin.site.register(Tag)
admin.site.register(AgeGroup)
admin.site.register(Vote)
