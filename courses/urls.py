from django.urls import path, include
from .views import CourseView, CourseAdminView, CourseRatingView, CreateCheckoutSessionView, stripe_webhook, LessonView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'courses', CourseView, basename='courses')
router.register(r'admin', CourseAdminView, basename='courses-admin')
router.register(r'rating', CourseRatingView, basename='rating')
router.register(r'lesson', LessonView, basename='lesson')

urlpatterns = [
    path('', include(router.urls)),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),
]
