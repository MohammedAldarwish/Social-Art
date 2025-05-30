from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    
    def __str__(self):
        return self.username
    
        
   
class Follower(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following' ,on_delete=models.CASCADE)
    followed_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers' ,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'followed_user']
        
    def __str__(self):
        return f"{self.user} follows {self.followed_user}"
    
 
    

class MyProfileModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    follow = models.ForeignKey(Follower, on_delete=models.CASCADE, null=True, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default_avatar.jpg',
        blank=True,
        null=True
        )
    

    created_at = models.DateTimeField(auto_now_add=True)    