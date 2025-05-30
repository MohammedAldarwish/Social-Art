from django.contrib import admin
from .models import Course, Enrollment, Payment, Lesson

admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Payment)
admin.site.register(Lesson)