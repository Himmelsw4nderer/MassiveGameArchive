
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()

class Game(models.Model):
    title = models.CharField(max_length=255)
    short_description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    markdown_content = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_created')
    difficulty_index = models.IntegerField(choices=[(i, i) for i in range(1, 11)], default=5)
    group_size_index = models.IntegerField(choices=[(i, i) for i in range(1, 11)], default=5)
    preperation_index = models.IntegerField(choices=[(i, i) for i in range(1, 11)], default=5)
    physical_index = models.IntegerField(choices=[(i, i) for i in range(1, 11)], default=5)
    duration_index = models.IntegerField(choices=[(i, i) for i in range(1, 11)], default=5)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('game_detail', kwargs={'slug': self.slug})
