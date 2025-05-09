from django import forms
from django.forms import inlineformset_factory
from django.core.validators import MinValueValidator
from django.utils.text import slugify

from .models import Game, Category, AgeGroup, GameMaterial, GameMaterialRequirement, GameVariant

class GameForm(forms.ModelForm):
    """Form for creating and editing games with markdown support"""
    
    class Meta:
        model = Game
        fields = [
            'title', 'description', 'rules', 'preparation', 'tips',
            'min_players', 'max_players', 'duration', 'difficulty',
            'categories', 'age_groups', 'indoor', 'outdoor'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'rules': forms.Textarea(attrs={'rows': 10}),
            'preparation': forms.Textarea(attrs={'rows': 5}),
            'tips': forms.Textarea(attrs={'rows': 5}),
            'categories': forms.SelectMultiple(attrs={'class': 'select2'}),
            'age_groups': forms.SelectMultiple(attrs={'class': 'select2'}),
        }
        help_texts = {
            'description': 'Eine kurze Zusammenfassung des Spiels',
            'rules': 'Die Spielregeln im Detail',
            'preparation': 'Vorbereitungsschritte für Spielleiter',
            'tips': 'Hilfreiche Tipps und Hinweise für die Durchführung',
            'min_players': 'Minimale Anzahl von Spielern',
            'max_players': 'Maximale Anzahl von Spielern (leer lassen für unbegrenzt)',
            'duration': 'Ungefähre Spieldauer in Minuten',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Check that at least one location is selected
        indoor = cleaned_data.get('indoor')
        outdoor = cleaned_data.get('outdoor')
        
        if not indoor and not outdoor:
            raise forms.ValidationError(
                'Bitte wähle mindestens einen Spielort (innen oder außen) aus.'
            )
        
        # Ensure min_players <= max_players if max_players is provided
        min_players = cleaned_data.get('min_players')
        max_players = cleaned_data.get('max_players')
        
        if min_players and max_players and min_players > max_players:
            raise forms.ValidationError(
                'Die minimale Spieleranzahl darf nicht größer sein als die maximale Spieleranzahl.'
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Auto-generate slug if this is a new game
        if not instance.pk and not instance.slug:
            slug = slugify(instance.title)
            # Ensure slug is unique
            orig_slug = slug
            counter = 1
            while Game.objects.filter(slug=slug).exists():
                slug = f"{orig_slug}-{counter}"
                counter += 1
            instance.slug = slug
        
        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many relationships
            
        return instance


class MaterialRequirementForm(forms.ModelForm):
    """Form for adding material requirements to a game"""
    
    # Add a field to create new materials on the fly
    new_material_name = forms.CharField(
        required=False, 
        label='Neues Material hinzufügen',
        help_text='Falls das Material nicht in der Liste ist'
    )
    
    class Meta:
        model = GameMaterialRequirement
        fields = ['material', 'quantity', 'required']
        widgets = {
            'material': forms.Select(attrs={'class': 'select2'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        material = cleaned_data.get('material')
        new_material_name = cleaned_data.get('new_material_name')
        
        if not material and not new_material_name:
            raise forms.ValidationError(
                'Bitte wähle ein Material aus oder füge ein neues hinzu.'
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # If a new material was specified, create it
        new_material_name = self.cleaned_data.get('new_material_name')
        if new_material_name and not self.cleaned_data.get('material'):
            material, created = GameMaterial.objects.get_or_create(
                name=new_material_name
            )
            instance.material = material
        
        if commit:
            instance.save()
        
        return instance


# Create a formset for managing multiple materials at once
MaterialRequirementFormSet = inlineformset_factory(
    Game, 
    GameMaterialRequirement,
    form=MaterialRequirementForm,
    extra=1,
    can_delete=True
)


class GameVariantForm(forms.ModelForm):
    """Form for adding variants to a game"""
    
    class Meta:
        model = GameVariant
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'markdown-editor'})
        }


class GameRatingForm(forms.Form):
    """Form for rating and reviewing a game"""
    
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        required=True,
        label='Bewertung',
        widget=forms.RadioSelect(choices=[(i, i) for i in range(1, 6)])
    )
    
    review = forms.CharField(
        required=False,
        label='Kommentar',
        widget=forms.Textarea(attrs={'rows': 3})
    )


class GameFilterForm(forms.Form):
    """Form for filtering games in the game list view"""
    
    q = forms.CharField(
        required=False,
        label='Suche',
        widget=forms.TextInput(attrs={'placeholder': 'Spielname oder Beschreibung'})
    )
    
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'select2'})
    )
    
    age_groups = forms.ModelMultipleChoiceField(
        queryset=AgeGroup.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'select2'})
    )
    
    min_players = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Min'})
    )
    
    max_players = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Max'})
    )
    
    min_duration = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Min'})
    )
    
    max_duration = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Max'})
    )
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Leicht'),
        ('medium', 'Mittel'),
        ('hard', 'Schwer'),
    ]
    
    difficulty = forms.MultipleChoiceField(
        choices=DIFFICULTY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    indoor = forms.BooleanField(required=False)
    outdoor = forms.BooleanField(required=False)
    
    SORT_CHOICES = [
        ('newest', 'Neueste zuerst'),
        ('rating', 'Beste Bewertung'),
        ('popularity', 'Beliebtheit'),
        ('title', 'Alphabetisch (A-Z)'),
        ('duration', 'Kurze Spieldauer zuerst'),
    ]
    
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='newest'
    )