from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AgeGroup(models.Model):
    name = models.CharField(max_length=50)
    min_age = models.PositiveIntegerField()
    max_age = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["min_age"]

    def __str__(self):
        if self.max_age:
            return f"{self.name} ({self.min_age}-{self.max_age} Jahre)"
        return f"{self.name} (ab {self.min_age} Jahre)"


class GameMaterial(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Game(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Leicht'),
        ('medium', 'Mittel'),
        ('hard', 'Schwer'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    rules = models.TextField()
    preparation = models.TextField(blank=True)
    tips = models.TextField(blank=True)
    
    min_players = models.PositiveIntegerField(default=2)
    max_players = models.PositiveIntegerField(null=True, blank=True)
    duration = models.PositiveIntegerField(help_text="Ungefähre Spieldauer in Minuten")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    
    categories = models.ManyToManyField(Category, related_name='games')
    age_groups = models.ManyToManyField(AgeGroup, related_name='games')
    materials = models.ManyToManyField(GameMaterial, through='GameMaterialRequirement')
    
    indoor = models.BooleanField(default=True, help_text="Spiel ist für drinnen geeignet")
    outdoor = models.BooleanField(default=False, help_text="Spiel ist für draußen geeignet")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='games_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('wiki:game_detail', kwargs={'slug': self.slug})


class GameMaterialRequirement(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    material = models.ForeignKey(GameMaterial, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50, blank=True, help_text="z.B. '2 Stück' oder 'pro Spieler 1'")
    required = models.BooleanField(default=True, help_text="Ist das Material zwingend notwendig?")
    
    class Meta:
        unique_together = ['game', 'material']
    
    def __str__(self):
        return f"{self.material.name} für {self.game.title}"


class GameImage(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='game_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-is_primary", "-uploaded_at"]

    def __str__(self):
        return f"Bild für {self.game.title}"


class GameVariant(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='variants')
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} (Variante von {self.game.title})"


class GameRating(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 star rating
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['game', 'user']
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.user.username}: {self.rating} Sterne für {self.game.title}"

    def save(self, *args, **kwargs):
        # Update the game's average rating when a new rating is saved
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Recalculate average
        avg = self.game.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
        count = self.game.ratings.count()
        
        # Update the game object
        self.game.avg_rating = avg
        self.game.rating_count = count
        self.game.save(update_fields=['avg_rating', 'rating_count'])