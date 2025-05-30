from rest_framework import viewsets , permissions
from .serializer import CourseSerializer, LessonSerializer, EnrollmentSerializer, PaymentSerializer, CourseAdminSerializer, CourseRatingSerializer
from .models import Course, CourseRating, Enrollment, Payment, Lesson
from .permission__ import IsInstructorOwner
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

import stripe
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from rest_framework.exceptions import PermissionDenied

from django.shortcuts import get_object_or_404

stripe.api_key = settings.STRIPE_SECRET_KEY

class CourseView(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_approved=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructorOwner]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)
               

class CourseAdminView(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_approved=False)
    serializer_class = CourseAdminSerializer
    permission_classes = [permissions.IsAdminUser]   
    http_method_names =  ['get', 'patch']    
    
    
    def partial_update(self, request, *args, **kwargs):
        if 'is_approved' not in request.data:
            return Response({"error": "Update Only for is_approved field"}, status=400)
        return super().partial_update(request, *args, **kwargs)
    
                                
                                
class CourseRatingView(viewsets.ModelViewSet):
    queryset = CourseRating.objects.all()
    serializer_class = CourseRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    

    def get_queryset(self):
        course_id = self.request.query_params.get('course')
        if course_id:
            return CourseRating.objects.filter(course_id=course_id)
        return CourseRating.objects.none()
    
    
    

class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        course_id = request.data.get("course_id")
        course = Course.objects.get(id=course_id)
        
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response({'detail': 'You are registered in this course'}, status=400)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(course.price * 100),  
                    'product_data': {
                        'name': course.title,
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:8000/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:8000/cancel',
            metadata={
                "course_id": str(course.id),
                "user_id": str(request.user.id),
            }
        )

        return Response({'checkout_url': session.url})
    
    

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        course_id = session['metadata']['course_id']
        user_id = session['metadata']['user_id']

        try:
            user = User.objects.get(id=user_id)
            course = Course.objects.get(id=course_id)
        except (User.DoesNotExist, Course.DoesNotExist):
            return HttpResponse(status=404)

        enrollment, created = Enrollment.objects.get_or_create(student=user, course=course)

        Payment.objects.create(
            enrollment=enrollment,
            amount=course.price,
            is_paid=True,
            payment_id=session['payment_intent'],
        )

    return HttpResponse(status=200)


class LessonView(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.request.query_params.get('course')
        if not course_id:
            return Lesson.objects.none()

        course = get_object_or_404(Course, id=course_id)

        if course.instructor == self.request.user:
            return course.lessons.all()

        if not course.price:
            return course.lessons.filter(is_published=True)
       
        enrollment = Enrollment.objects.filter(student=self.request.user, course=course).first()
        if enrollment and hasattr(enrollment, 'payment') and enrollment.payment.is_paid:
            return course.lessons.filter(is_published=True)


        return Lesson.objects.none()
    
    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if not course:
            raise ValidationError("Course is required.")

        if course.instructor != self.request.user:
            raise PermissionDenied("You are not the instructor of this course.")
        
        if not course.is_approved:
            raise PermissionDenied("Cannot add lessons to an unapproved course.")
        serializer.save()
