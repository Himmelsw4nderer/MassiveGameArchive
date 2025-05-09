from django.contrib import admin
from .models import Game, Category, AgeGroup, GameMaterial, GameImage, GameVariant, GameRating, GameMaterialRequirement


class GameMaterialRequirementInline(admin.TabularInline):
    model = GameMaterialRequirement
    extra = 1


class GameImageInline(admin.TabularInline):
    model = GameImage
    extra = 1


class GameVariantInline(admin.TabularInline):
    model = GameVariant
    extra = 0


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_categories', 'get_age_groups', 'min_players', 'max_players', 
                    'duration', 'difficulty', 'indoor', 'outdoor', 'created_by', 'created_at', 'avg_rating')
    list_filter = ('categories', 'age_groups', 'difficulty', 'indoor', 'outdoor', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GameMaterialRequirementInline, GameImageInline, GameVariantInline]
    filter_horizontal = ('categories', 'age_groups')
    
    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = "Kategorien"
    
    def get_age_groups(self, obj):
        return ", ".join([str(age_group) for age_group in obj.age_groups.all()])
    get_age_groups.short_description = "Altersgruppen"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_age', 'max_age')
    list_filter = ('min_age', 'max_age')
    search_fields = ('name',)


@admin.register(GameMaterial)
class GameMaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(GameImage)
class GameImageAdmin(admin.ModelAdmin):
    list_display = ('game', 'caption', 'is_primary', 'uploaded_at')
    list_filter = ('is_primary', 'uploaded_at')
    search_fields = ('game__title', 'caption')


@admin.register(GameVariant)
class GameVariantAdmin(admin.ModelAdmin):
    list_display = ('title', 'game', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description', 'game__title')


@admin.register(GameRating)
class GameRatingAdmin(admin.ModelAdmin):
    list_display = ('game', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('game__title', 'user__username', 'review')