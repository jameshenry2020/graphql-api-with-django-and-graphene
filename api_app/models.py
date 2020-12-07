from django.db import models
from django.conf import settings

# Create your models here.
User=settings.AUTH_USER_MODEL

class Question(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField(blank=True, null=True)
    posted_by=models.ForeignKey(User, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title


class Answers(models.Model):
     posted_by=models.ForeignKey(User, on_delete=models.CASCADE)
     answer=models.TextField()
     question=models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)