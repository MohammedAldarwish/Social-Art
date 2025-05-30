from .models import CustomUser, Follower, MyProfileModel
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterTestCase(APITestCase):
    def test_register_success(self):
        url = reverse('register')
        data = {
            "email": "test@gmail.com",
            "username": "test",
            "password": "A.123456789",
            "password_confirm": "A.123456789"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(email='test@gmail.com').exists())
    
    def test_register_password_mismatch(self):
        url = reverse('register')
        data = {
            "email": "test2@gmail.com",
            "username": "test2",
            "password": "A.123456789",
            "password_confirm": "A.12345678"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The Passwords Do not match", str(response.data))
        
                          
                        
class LoginTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="login@gmail.com",
            username="login",
            password="A.123456789"
        )
    
    def test_login_success(self):
        url = reverse('login')
        data = {
            "username": "login",
            "password": "A.123456789"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        
    def test_login_fail(self):
        url = reverse('login')
        data = {
            "username": "loginuser",
            "password": "wrongpass"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
class LogoutTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="mohammed@gmail.com",
            username="mohammed",
            password="A.123456789"
        )
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        
    def test_logout_success(self):
        url = reverse('logout')
        response = self.client.post(url, {"refresh": self.refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
    
    def test_logout_invalid_token(self):
        url = reverse('logout')
        response = self.client.post(url, {"refresh": "invalid_token"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        


class FollowTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='A.123456789'
        )
        self.other_user = CustomUser.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='A.123456789'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        self.url = reverse('follow')

    def test_cannot_follow_self(self):
        response = self.client.post(self.url, data={'followed_user': self.user.id})
        self.assertEqual(response.status_code, 400)
        self.assertIn('You cannot follow yourself', str(response.data))

    def test_cannot_follow_twice(self):
        self.client.post(self.url, data={'followed_user': self.other_user.id})
        response = self.client.post(self.url, data={'followed_user': self.other_user.id})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Already following', str(response.data))

    def test_unfollow_success(self):
        self.client.post(self.url, data={'followed_user': self.other_user.id})
        response = self.client.delete(self.url, data={'followed_user': self.other_user.id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Unfollowed', str(response.data))
        self.assertFalse(Follower.objects.filter(user=self.user, followed_user=self.other_user).exists())



class ProfileTestCase(APITestCase):
   def setUp(self):
    self.user1 = CustomUser.objects.create_user(email="user1@test.com", username="user1", password="pass1234A.")
    self.user2 = CustomUser.objects.create_user(email="user2@test.com", username="user2", password="pass1234A.")
    MyProfileModel.objects.filter(user=self.user1).delete()
    MyProfileModel.objects.filter(user=self.user2).delete()
    MyProfileModel.objects.create(user=self.user2, bio="Hello user2")

    refresh = RefreshToken.for_user(self.user1)
    self.access_token = str(refresh.access_token)
    self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_get_my_profile(self):
        self.client.login(username="user1", password="pass1234A.")
        url = reverse('my-profile')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user1.id)  

    def test_get_other_profile(self):
        url = reverse('other-profile', kwargs={'username': 'user2'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], "Hello user2")

    def test_get_other_profile_not_found(self):
        url = reverse('other-profile', kwargs={'username': 'nonexistent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)