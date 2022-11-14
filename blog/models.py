from django.db import models


# Create your models here.
class Post(models.Model):
    author = models.ForeignKey('auth.User', related_name='posts', on_delete=models.CASCADE)
    publish_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=255, blank=True)


class ReaderToAuthor(models.Model):
    reader = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)


class ReadedPost(models.Model):
    reader = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)