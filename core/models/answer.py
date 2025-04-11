from django.db import models
from django.contrib.auth.models import User
from .question import Question


class Answer(models.Model):
    content = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    likes = models.ManyToManyField(User, related_name='liked_answers', blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return f"Answer by {self.author.username} on {self.question.title}"
    
    def total_likes(self):
        return self.likes.count() 