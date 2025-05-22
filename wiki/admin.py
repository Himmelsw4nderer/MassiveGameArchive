from django.contrib import admin
from wiki.models import Game
from django.utils.text import slugify
import hashlib

class GameAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = hashlib.sha256(str(obj).encode('utf-8')).hexdigest()
        super().save_model(request, obj, form, change)

admin.site.register(Game, GameAdmin)
