from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import RegisterSerializer, MyTokenObtainPairSerializer, MyProfileSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from .models import CustomUser, Follower, MyProfileModel
from rest_framework.generics import RetrieveAPIView
from rest_framework import generics
#from .filters import UserFilter
from rest_framework import filters


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response ({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'email': user.email,
                    'username': user.username
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    

class LogoutView(APIView):
    permissions = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"},status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class FollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
  
           
    
    def post(self, request):
        followed_id = request.data.get('followed_user')
        followed_user = get_object_or_404(CustomUser, id=followed_id)
        
        if followed_user == request.user:
            return Response({'detail': 'You cannot follow yourself!'}, status=400)
        
        if Follower.objects.filter(user=request.user, followed_user=followed_user).exists():
            return Response({'detail': 'Already following'}, status=400)
         
        Follower.objects.create(user=request.user, followed_user=followed_user)
        return Response({'detail': 'Followed'})
    
    def delete(self, request, *args, **kwargs):
        followed_id = request.data.get('followed_user')
        followed_user = get_object_or_404(CustomUser, id=followed_id)
        
        follow = Follower.objects.filter(user=request.user, followed_user=followed_user).first()
        if follow:
            follow.delete()
            return Response({'detail': 'Unfollowed'})
        return Response({'detail': 'Not following'}, status=400)
    
    
    def get(self, request):
        user_id = request.query_params.get('user_id')
        mode = request.query_params.get('mode')  # 'followers' or 'following'

        if not user_id or mode not in ['followers', 'following']:
            return Response({'detail': 'Please provide user_id and mode (followers or following)'}, status=400)

        if mode == 'followers':
            followers = Follower.objects.filter(followed_user_id=user_id)
            data = [{'id': f.user.id, 'username': f.user.username} for f in followers]
        else:
            following = Follower.objects.filter(user_id=user_id)
            data = [{'id': f.followed_user.id, 'username': f.followed_user.username} for f in following]

        return Response(data)
    
    
class MyProfileView(RetrieveAPIView):
    serializer_class = MyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        profile, created = MyProfileModel.objects.get_or_create(user=user)
        return profile
    
    

class OtherProfileView(RetrieveAPIView):
    serializer_class = MyProfileSerializer
    
    def get_object(self):
        username = self.kwargs['username']
        return get_object_or_404(MyProfileModel, user__username=username)
    
    
class UserSearchView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']