# chat/models.py
from django.db import models

class Chat(models.Model):
    question = models.TextField()
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.question[:50]} | A: {self.answer[:50]}"
