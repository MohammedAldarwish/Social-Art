'''from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.dispatch import receiver
from django.apps import apps
from django.contrib.contenttypes.models import ContentType


@receiver(post_migrate)
def setup_instructor_group(sender, **kwargs):
    group, _ = Group.objects.get_or_create(name='instructor')

    Course = apps.get_model('courses', 'Course')
    content_type = ContentType.objects.get_for_model(Course)

    perms = Permission.objects.filter(
        content_type=content_type,
        codename__in=[
            'add_course',      
            'change_course',   
            'delete_course'
        ]
    )

    group.permissions.set(perms) '''