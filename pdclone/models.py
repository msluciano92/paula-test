from django.db import models
from django.utils.timezone import now

# Create your models here.
class CustomUser(models.Model):
    username = models.CharField(max_length=30, null=True)
    name = models.CharField(max_length=30, null=True)
    banner = models.ImageField(null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True)
    created_date = models.DateTimeField(default=now, editable=False)
    description = models.CharField(default=" ", max_length=1000)


class Community(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    banner = models.ImageField(null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True)
    subscribers = models.ManyToManyField(CustomUser)

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=30)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default="", related_name="posts")
    body = models.CharField(max_length=1000)
    url = models.URLField(blank=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, default="", related_name="posts")
    points = models.IntegerField(default=1)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    savedBy = models.ManyToManyField(CustomUser)

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default="", related_name="comments")
    body = models.CharField(max_length=1000)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    finalvotes = models.IntegerField(default=0)
    saved_by_user = models.BooleanField(default=False)
    savedBy = models.ManyToManyField(CustomUser)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)