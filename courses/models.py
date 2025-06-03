from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid
from django.contrib.auth.models import Group
from django.core.validators import MaxValueValidator, MinValueValidator

class Course(models.Model):
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_approved = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
            
    def __str__(self):
        return self.title
    

class CourseImages(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to = 'course_images/')
    
    def __str__(self):
        return f"image for {self.course.title}"
    

class CourseRating(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['course', 'user']
        
    def __str__(self):
        return f"{self.user} rated {self.course} - {self.rating}"
    


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=1)
    video_file = models.FileField(upload_to='videos/')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return f"{self.course.title} - {self.title}"    
    

class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')        
    course = models.ForeignKey(Course , on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'course')
        
    def __str__(self):
        return f"{self.student} enrolled in {self.course}"
    
    
class Payment(models.Model):
    order_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def platform_fee(self):
        return (self.amount * Decimal('0.10')).quantize(Decimal('0.01'))
    
    def instructor_share(self):
        return (self.amount * Decimal('0.90')).quantize(Decimal('0.01'))
    
    def __str__(self):
        return f"{self.enrollment.student} bought a course {self.enrollment.course} price {self.amount}"
    
    
class InstructorDashboard(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE) 
    errollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Dashboard for {self.user} - {self.course.title}"
    