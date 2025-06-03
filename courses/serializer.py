from rest_framework import serializers
from .models import Course, Lesson, Enrollment, Payment, CourseImages, CourseRating, InstructorDashboard


class ImageCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseImages
        fields = ['image']

class CourseSerializer(serializers.ModelSerializer):
    images = ImageCourseSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['instructor', 'title', 'description', 'price', 'images']
        read_only_fields = ['instructor']
        
    def create(self, validated_data):
        images_data = self.context['request'].FILES.getlist('images')
        course = Course.objects.create(**validated_data)
        for image in images_data:
            CourseImages.objects.create(course=course, image=image)
        return course

class CourseRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRating
        fields = ['id', 'course', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        course = attrs.get('course')

        if not Enrollment.objects.filter(student=user, course=course).exists():
            raise serializers.ValidationError('You must be enrolled in the course to rate it.')

        if CourseRating.objects.filter(course=course, user=user).exists():
            raise serializers.ValidationError('You have already rated this course.')

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

# Don't Forget to fix the bug
class CourseAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['instructor','title', 'description', 'price', 'is_approved']
        read_only_fields = ['instructor', 'title', 'description', 'price']          
        
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['created_at']


        
        
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'enrolled_at']
        read_only_fields = ['enrolled_at']
        
        
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['order_id', 'enrollment', 'amount', 'is_paid', 'payment_id']
        read_only_fields = ['order_id', 'is_paid']
        


class InstructorDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorDashboard
        fields = ['user', 'course', 'errollment', 'created_at']
        read_only_fields = ['created_at']