from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, MyProfileModel


# to create profile automatically when create account 
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        MyProfileModel.objects.create(user=instance)
