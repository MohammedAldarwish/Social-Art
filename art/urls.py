from django.urls import path, include
from .views import ArtView, CommentViewSet, LikeViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('art', ArtView, basename='art')
router.register('comment', CommentViewSet, basename='comment')
router.register('like', LikeViewSet, basename='like')



urlpatterns = router.urls

