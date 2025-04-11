from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.postgres.search import SearchVectorField


class Question(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    search_vector = SearchVectorField(null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('question_detail', kwargs={'pk': self.pk}) 