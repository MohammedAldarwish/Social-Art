from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import CustomUser
from .models import ArtLike, Comment, ArtModel, Category

class ArtTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", email="test@test.com", password="test1234A.")
        self.client.force_authenticate(user=self.user)  # توثيق مباشر بدون login

    def test_create_art(self):
        url = reverse('art-list')
        category1 = Category.objects.create(name="Painting")
        category2 = Category.objects.create(name="Sketch")
        data = {
            "title": "My First Art",
            "description": "Cool art!",
            "categories": [category1.id, category2.id],  # لازم ترسل قائمة
        }
        response = self.client.post(url, data, format='json')
        print(response.data)  # لو تبغى تشوف الخطأ
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ArtModel.objects.count(), 1)
        self.assertEqual(ArtModel.objects.first().user, self.user)

class CommentTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="commenter", email="comment@test.com", password="test1234A.")
        self.client.force_authenticate(user=self.user)
        self.art = ArtModel.objects.create(user=self.user, title="Art", description="Desc")
        self.category = Category.objects.create(name="Painting")
        self.art.categories.add(self.category)

    def test_create_comment(self):
        url = reverse('comment-list')
        data = {
            "content": "Nice work!",  
            "art_post": self.art.id,
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

class LikeTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="liker", email="like@test.com", password="test1234A.")
        self.client.force_authenticate(user=self.user)
        self.art = ArtModel.objects.create(user=self.user, title="Art", description="Desc")
        self.category = Category.objects.create(name="Painting")
        self.art.categories.add(self.category)

    def test_like_post(self):
        url = reverse('like-list')
        data = {
            "art_post": self.art.id,
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ArtLike.objects.count(), 1)

    def test_duplicate_like_fails(self):
        ArtLike.objects.create(user=self.user, art_post=self.art)
        url = reverse('like-list')
        data = {"art_post": self.art.id}
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
