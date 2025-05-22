
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Tag(models.Model):
    """
    Model representing a tag for categorizing games.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class AgeGroup(models.Model):
    """
    Model representing different age groups for games.
    """
    name = models.CharField(max_length=50, unique=True)
    min_age = models.PositiveSmallIntegerField(default=0)
    max_age = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        if self.max_age:
            return f"{self.name} ({self.min_age}-{self.max_age} years)"
        return f"{self.name} ({self.min_age}+ years)"

    class Meta:
        ordering = ['min_age']


class Resource(models.Model):
    """
    Model representing an external resource (like images, documents) for a game.
    """
    TYPE_CHOICES = [
        ('image', 'Image'),
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    url = models.URLField(max_length=500)
    description = models.TextField(blank=True)
    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name='resources')

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"

    class Meta:
        ordering = ['title']


class Game(models.Model):
    """
    Model representing a game in the archive.
    """
    COMPLEXITY_CHOICES = [
        (1, 'Very Simple'),
        (2, 'Simple'),
        (3, 'Moderate'),
        (4, 'Complex'),
        (5, 'Very Complex'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField(help_text="Markdown formatted game description and rules")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationships
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_games')
    tags = models.ManyToManyField(Tag, related_name='games', blank=True)
    age_groups = models.ManyToManyField(AgeGroup, related_name='games', blank=True)
    parent_game = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='variants')

    # Game properties
    complexity = models.PositiveSmallIntegerField(
        choices=COMPLEXITY_CHOICES,
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    # Popularity metrics
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    # Additional properties
    is_variant = models.BooleanField(default=False)
    variant_name = models.CharField(max_length=200, blank=True,
                                   help_text="Name of this variant (if this is a variant)")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Set is_variant flag based on parent_game
        if self.parent_game and not self.is_variant:
            self.is_variant = True

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('game_detail', args=[str(self.slug)])

    @property
    def score(self):
        """Calculate Reddit-like score: upvotes - downvotes"""
        return self.upvotes - self.downvotes

    @property
    def popularity_index(self):
        """
        Calculate a popularity index based on upvotes, view count, and comment count
        This is a placeholder implementation that can be enhanced later
        """
        comment_count = self.comments.count()
        # Simple weighted formula
        return (self.score * 3) + (comment_count * 2) + (self.view_count * 0.1)

    def __str__(self):
        if self.is_variant and self.variant_name:
            return f"{self.title} - {self.variant_name}"
        return self.title

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
            models.Index(fields=['upvotes']),
        ]


class GameVote(models.Model):
    """
    Model to track user votes on games to prevent duplicate voting
    """
    VOTE_CHOICES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
        ('none', 'No Vote'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_votes')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='user_votes')
    vote_type = models.CharField(max_length=4, choices=VOTE_CHOICES, default='none')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'game')
        indexes = [
            models.Index(fields=['user', 'game']),
        ]

    def __str__(self):
        return f"{self.user.username}'s {self.get_vote_type_display()} on {self.game.title}"


class Comment(models.Model):
    """
    Model representing comments on games.
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='game_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Comment metrics
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)

    @property
    def score(self):
        """Calculate Reddit-like score: upvotes - downvotes"""
        return self.upvotes - self.downvotes

    def __str__(self):
        return f"Comment by {self.author.username if self.author else 'Anonymous'} on {self.game.title}"

    class Meta:
        ordering = ['-created_at']


class CommentVote(models.Model):
    """
    Model to track user votes on comments to prevent duplicate voting
    """
    VOTE_CHOICES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
        ('none', 'No Vote'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_votes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='user_votes')
    vote_type = models.CharField(max_length=4, choices=VOTE_CHOICES, default='none')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')
        indexes = [
            models.Index(fields=['user', 'comment']),
        ]

    def __str__(self):
        return f"{self.user.username}'s {self.get_vote_type_display()} on comment {self.comment.id}"


class VariantCollection(models.Model):
    """
    Model representing a collection of game variants.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    base_game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='variant_collections')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='variant_collections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (for {self.base_game.title})"

    class Meta:
        ordering = ['name']
