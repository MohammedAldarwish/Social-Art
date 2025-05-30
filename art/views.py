from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .serializer import ArtSerializer, CreateCommentSerializer, CreateLikeSerializer
from .models import ArtModel, Comment, ArtLike
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from .permissions import CanDelete
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from django.core.cache import cache

class ArtView(ModelViewSet):
    queryset = ArtModel.objects.all().order_by('-posted_at')
    serializer_class = ArtSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
class CommentViewSet(ModelViewSet):
    serializer_class = CreateCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, CanDelete]

    def get_queryset(self):
        post_id = self.request.query_params.get('art_post')
        if not post_id:
            return Comment.objects.none()
        return Comment.objects.filter(art_post=post_id)

    def list(self, request, *args, **kwargs):
        post_id = request.query_params.get('art_post')
        if not post_id:
            return Response([])

        cache_key = f"comments_artpost_{post_id}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=60*5)
        return Response(serializer.data)

    def perform_create(self, serializer):
        art_post_id = self.request.data.get('art_post')
        art_post = get_object_or_404(ArtModel, id=art_post_id)
        serializer.save(user=self.request.user, art_post=art_post)

        cache_key = f"comments_artpost_{art_post_id}"
        cache.delete(cache_key)


class LikeViewSet(ModelViewSet):
    serializer_class = CreateLikeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, CanDelete]

    def get_queryset(self):
        post_id = self.request.query_params.get('art_post')
        if not post_id:
            return ArtLike.objects.none()
        return ArtLike.objects.filter(art_post=post_id)

    def list(self, request, *args, **kwargs):
        post_id = request.query_params.get('art_post')
        if not post_id:
            return Response([])

        cache_key = f"likes_artpost_{post_id}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=60*5)
        return Response(serializer.data)

    def perform_create(self, serializer):
        art_post_id = self.request.data.get('art_post')
        art_post = get_object_or_404(ArtModel, id=art_post_id)
        if ArtLike.objects.filter(user=self.request.user, art_post=art_post).exists():
            raise ValidationError('You already liked this post.')
        serializer.save(user=self.request.user, art_post=art_post)

        cache_key = f"likes_artpost_{art_post_id}"
        cache.delete(cache_key)
