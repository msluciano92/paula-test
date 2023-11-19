from django.contrib import admin
from .models import CustomUser, Post, Community, Comment

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Post)
admin.site.register(Community)
admin.site.register(Comment)