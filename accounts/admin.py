from django.contrib import admin
from .models import CustomUser, Follower

admin.site.register(CustomUser)
admin.site.register(Follower) 