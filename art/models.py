from django.db import models
from django.contrib.auth import get_user_model


class Category(models.Model):
    name = models.CharField(max_length=120)

    
    def __str__(self):
        return self.name
    

User = get_user_model()
class ArtModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE ,related_name='art_posts')
    title = models.CharField(max_length=120)
    description = models.TextField()
    categories = models.ManyToManyField(Category)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    
class ArtImage(models.Model):
    art = models.ForeignKey(ArtModel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='art_images/')
    
    def __str__(self):
        return f"Image for {self.art.title}"
    


class ArtLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    art_post = models.ForeignKey(ArtModel, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'art_post')
        
    def __str__(self):
        return f"{self.user.username} liked {self.art_post.title}"
    
    
        
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    art_post = models.ForeignKey(ArtModel, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} on {self.art_post.title}"
    