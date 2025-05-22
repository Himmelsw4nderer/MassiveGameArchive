
from django.contrib import admin
from .models import (
    Game, Tag, AgeGroup, Resource, GameVote,
    Comment, VariantCollection, CommentVote
)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_age', 'max_age')
    list_filter = ('min_age', 'max_age')
    search_fields = ('name',)

class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 1

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_variant', 'complexity', 'upvotes', 'created_at', 'creator')
    list_filter = ('is_variant', 'complexity', 'age_groups', 'tags', 'created_at')
    search_fields = ('title', 'content', 'variant_name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    inlines = [ResourceInline]
    filter_horizontal = ('tags', 'age_groups')

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'creator')
        }),
        ('Metadata', {
            'fields': ('tags', 'age_groups', 'complexity')
        }),
        ('Variant Information', {
            'fields': ('is_variant', 'parent_game', 'variant_name'),
        }),
        ('Statistics', {
            'fields': ('upvotes', 'downvotes', 'view_count'),
        }),
    )

@admin.register(GameVote)
class GameVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'vote_type', 'created_at')
    list_filter = ('vote_type', 'created_at')
    search_fields = ('user__username', 'game__title')
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('game', 'author', 'parent', 'created_at', 'upvotes')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'game__title')
    date_hierarchy = 'created_at'

@admin.register(CommentVote)
class CommentVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'vote_type', 'created_at')
    list_filter = ('vote_type', 'created_at')
    search_fields = ('user__username',)
    date_hierarchy = 'created_at'

@admin.register(VariantCollection)
class VariantCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_game', 'creator', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'base_game__title')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
