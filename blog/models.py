from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    readers = models.ManyToManyField('self', related_name='followers', symmetrical=False)


class Post(models.Model):
    author = models.ForeignKey(CustomUser, related_name='posts', on_delete=models.CASCADE)
    publish_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50, blank=False)
    description = models.TextField(max_length=140, blank=True)

    class Meta:
        ordering = ['-publish_date']


class Feed(models.Model):
    recipient = models.ForeignKey(CustomUser, related_name='new_posts', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='feed', on_delete=models.CASCADE)
    post_readed = models.BooleanField(default=False)
