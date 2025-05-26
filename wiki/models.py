
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet

User = get_user_model()

class Game(models.Model):
    title = models.CharField(max_length=255)
    short_description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    markdown_content = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_created')
    created_at = models.DateTimeField(auto_now_add=True)
    difficulty_index = models.IntegerField(choices=[(i, i) for i in range(1, 11)], default=5)
    group_size_index = models.IntegerField(choices=[(i, i) for i in range(1, 11)], default=5)
    preperation_index = models.IntegerField(choices=[(i, i) for i in range(1, 11)], default=5)
    physical_index = models.IntegerField(choices=[(i, i) for i in range(1, 11)], default=5)
    duration_index = models.IntegerField(choices=[(i, i) for i in range(1, 11)], default=5)
    tags = models.ManyToManyField('Tag', related_name='games', blank=True)
    age_groups = models.ManyToManyField('AgeGroup', related_name='games', blank=True)

    if TYPE_CHECKING:
        votes: 'QuerySet[Vote]'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_upvote_count(self):
        """Get the number of upvotes for this game."""
        return self.votes.filter(value=1).count()

    def get_downvote_count(self):
        """Get the number of downvotes for this game."""
        return self.votes.filter(value=-1).count()

    def get_age_groups(self):
        """Return a string representation of all age groups associated with this game."""
        age_groups = self.age_groups.all()
        return [str(age_group) for age_group in age_groups]

    def get_tags(self):
        """Return a string representation of all tags associated with this game."""
        tags = self.tags.all()
        return [str(tag) for tag in tags]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('game_detail', kwargs={'slug': self.slug})

class Tag(models.Model):
    name = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_all_tags(cls):
        tags = cls.objects.all()
        return [str(tag) for tag in tags]


class AgeGroup(models.Model):
    string_title = models.CharField(max_length=25, unique=True)
    minimum_age = models.IntegerField()
    maximum_age = models.IntegerField()

    def __str__(self):
        return f"{self.string_title} ({self.minimum_age}-{self.maximum_age})"

    @classmethod
    def get_all_age_groups(cls):
        age_groups = cls.objects.all()
        return [str(age_group) for age_group in age_groups]
class Vote(models.Model):
    VOTE_CHOICES = (
        (1, 'Upvote'),
        (-1, 'Downvote'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='votes')
    value = models.SmallIntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        return f"{self.user.username} - {'Upvoted' if self.value > 0 else 'Downvoted'} - {self.game.title}"
