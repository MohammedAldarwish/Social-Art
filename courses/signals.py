from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Course, InstructorDashboard


@receiver(post_save, sender=Course)
def create_instructor_dashboard(sender, instance, **kwargs):
    if instance.is_approved:
        InstructorDashboard.objects.get_or_create(
            create=instance,
            default={'user': instance.instructor}
        )