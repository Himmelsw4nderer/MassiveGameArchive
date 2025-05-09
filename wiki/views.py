from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.forms import modelformset_factory

from .models import (
    Game, Category, AgeGroup, GameRating, GameVariant, 
    GameMaterial, GameMaterialRequirement, GameImage
)
from .forms import (
    GameForm, MaterialRequirementFormSet, GameVariantForm, 
    GameRatingForm, GameFilterForm
)


def home(request):
    newest_games = Game.objects.all().order_by('-created_at')[:6]
    top_rated_games = Game.objects.all().order_by('-avg_rating')[:6]
    popular_categories = Category.objects.annotate(
        game_count=Count('games')
    ).order_by('-game_count')[:8]
    games_count = Game.objects.count()
    
    context = {
        'newest_games': newest_games,
        'top_rated_games': top_rated_games,
        'popular_categories': popular_categories,
        'games_count': games_count
    }
    
    return render(request, 'wiki/home.html', context)


class GameListView(ListView):
    model = Game
    template_name = 'wiki/game_list.html'
    context_object_name = 'games'
    paginate_by = 12

    def get_queryset(self):
        queryset = Game.objects.all()
        
        # Search by title or description
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            )
            
        # Filter by categories
        categories = self.request.GET.getlist('categories')
        if categories:
            queryset = queryset.filter(categories__id__in=categories).distinct()
            
        # Filter by age groups
        age_groups = self.request.GET.getlist('age_groups')
        if age_groups:
            queryset = queryset.filter(age_groups__id__in=age_groups).distinct()
            
        # Filter by number of players
        min_players = self.request.GET.get('min_players')
        if min_players:
            queryset = queryset.filter(min_players__gte=min_players)
            
        max_players = self.request.GET.get('max_players')
        if max_players:
            queryset = queryset.filter(
                Q(max_players__lte=max_players) | Q(max_players__isnull=True)
            )
            
        # Filter by duration
        min_duration = self.request.GET.get('min_duration')
        if min_duration:
            queryset = queryset.filter(duration__gte=min_duration)
            
        max_duration = self.request.GET.get('max_duration')
        if max_duration:
            queryset = queryset.filter(duration__lte=max_duration)
            
        # Filter by difficulty
        difficulty = self.request.GET.getlist('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty__in=difficulty)
            
        # Filter by location (indoor/outdoor)
        indoor = self.request.GET.get('indoor')
        if indoor == '1':
            queryset = queryset.filter(indoor=True)
            
        outdoor = self.request.GET.get('outdoor')
        if outdoor == '1':
            queryset = queryset.filter(outdoor=True)
            
        # Sorting
        sort_by = self.request.GET.get('sort', 'newest')
        if sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'rating':
            queryset = queryset.order_by('-avg_rating')
        elif sort_by == 'popularity':
            queryset = queryset.annotate(num_ratings=Count('ratings')).order_by('-num_ratings')
        elif sort_by == 'title':
            queryset = queryset.order_by('title')
        elif sort_by == 'duration':
            queryset = queryset.order_by('duration')
            
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['age_groups'] = AgeGroup.objects.all()
        
        # Add filter form
        if self.request.GET:
            context['filter_form'] = GameFilterForm(self.request.GET)
        else:
            context['filter_form'] = GameFilterForm()
        
        return context


class GameDetailView(DetailView):
    model = Game
    template_name = 'wiki/game_detail.html'
    context_object_name = 'game'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.get_object()
        
        # Get user's rating if logged in
        if self.request.user.is_authenticated:
            try:
                user_rating = GameRating.objects.get(
                    game=game,
                    user=self.request.user
                )
                context['user_rating'] = user_rating
                context['rating_form'] = GameRatingForm(initial={
                    'rating': user_rating.rating,
                    'review': user_rating.review
                })
            except GameRating.DoesNotExist:
                context['user_rating'] = None
                context['rating_form'] = GameRatingForm()
                
        # Get variant form if user is logged in
        if self.request.user.is_authenticated:
            context['variant_form'] = GameVariantForm()
        
        # Get related games (same categories)
        related_games = Game.objects.filter(
            categories__in=game.categories.all()
        ).exclude(pk=game.pk).distinct().order_by('-avg_rating')[:5]
        context['related_games'] = related_games
        
        return context


@login_required
@require_POST
def rate_game(request, slug):
    game = get_object_or_404(Game, slug=slug)
    form = GameRatingForm(request.POST)
    
    if form.is_valid():
        rating_value = form.cleaned_data['rating']
        review = form.cleaned_data['review']
        
        # Update or create the rating
        rating, created = GameRating.objects.update_or_create(
            game=game,
            user=request.user,
            defaults={
                'rating': rating_value,
                'review': review
            }
        )
        
        if created:
            messages.success(request, 'Deine Bewertung wurde hinzugefügt.')
        else:
            messages.success(request, 'Deine Bewertung wurde aktualisiert.')
    else:
        messages.error(request, 'Bitte korrigiere die Fehler im Formular.')
                
    return HttpResponseRedirect(game.get_absolute_url())


class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    form_class = GameForm
    template_name = 'wiki/game_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['material_formset'] = MaterialRequirementFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['material_formset'] = MaterialRequirementFormSet(instance=self.object)
            
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        material_formset = context['material_formset']
        
        form.instance.created_by = self.request.user
        
        if material_formset.is_valid():
            self.object = form.save()
            material_formset.instance = self.object
            material_formset.save()
            messages.success(self.request, 'Das Spiel wurde erfolgreich erstellt.')
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        return reverse('wiki:game_detail', kwargs={'slug': self.object.slug})


class GameUpdateView(LoginRequiredMixin, UpdateView):
    model = Game
    form_class = GameForm
    template_name = 'wiki/game_form.html'
    
    def get_queryset(self):
        # Only allow editing by the creator or staff
        if self.request.user.is_staff:
            return Game.objects.all()
        return Game.objects.filter(created_by=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['material_formset'] = MaterialRequirementFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['material_formset'] = MaterialRequirementFormSet(instance=self.object)
            
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        material_formset = context['material_formset']
        
        if material_formset.is_valid():
            self.object = form.save()
            material_formset.instance = self.object
            material_formset.save()
            messages.success(self.request, 'Das Spiel wurde erfolgreich aktualisiert.')
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        return reverse('wiki:game_detail', kwargs={'slug': self.object.slug})


@login_required
@require_POST
def add_variant(request, slug):
    game = get_object_or_404(Game, slug=slug)
    form = GameVariantForm(request.POST)
    
    if form.is_valid():
        variant = form.save(commit=False)
        variant.game = game
        variant.created_by = request.user
        variant.save()
        messages.success(request, 'Die Variante wurde erfolgreich hinzugefügt.')
    else:
        messages.error(request, 'Bitte korrigiere die Fehler im Formular.')
        
    return HttpResponseRedirect(game.get_absolute_url())


@login_required
def upload_game_images(request, slug):
    game = get_object_or_404(Game, slug=slug)
    
    # Check if the user has permission to add images
    if not request.user.is_staff and request.user != game.created_by:
        messages.error(request, 'Du hast keine Berechtigung, Bilder zu diesem Spiel hinzuzufügen.')
        return HttpResponseRedirect(game.get_absolute_url())
    
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        captions = request.POST.getlist('captions')
        is_primary = request.POST.get('is_primary')
        
        # Process each uploaded image
        for i, image_file in enumerate(images):
            caption = captions[i] if i < len(captions) else ""
            is_primary_image = (is_primary == str(i))
            
            # If this is set as primary, remove primary flag from other images
            if is_primary_image:
                game.images.filter(is_primary=True).update(is_primary=False)
            
            # Create the new image
            GameImage.objects.create(
                game=game,
                image=image_file,
                caption=caption,
                is_primary=is_primary_image
            )
        
        messages.success(request, f'{len(images)} Bilder wurden erfolgreich hochgeladen.')
        return HttpResponseRedirect(game.get_absolute_url())
        
    return render(request, 'wiki/upload_images.html', {'game': game})


@login_required
@require_POST
def delete_game_image(request, pk):
    image = get_object_or_404(GameImage, pk=pk)
    game = image.game
    
    # Check if the user has permission to delete images
    if not request.user.is_staff and request.user != game.created_by:
        messages.error(request, 'Du hast keine Berechtigung, dieses Bild zu löschen.')
        return HttpResponseRedirect(game.get_absolute_url())
    
    # Delete the image
    image.delete()
    messages.success(request, 'Das Bild wurde erfolgreich gelöscht.')
    
    return HttpResponseRedirect(game.get_absolute_url())