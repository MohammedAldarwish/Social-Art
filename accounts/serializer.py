from rest_framework import serializers
from .models import CustomUser, Follower, MyProfileModel

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from art.serializer import ArtSerializer

class RegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'password', 'password_confirm']
        extra_kwargs = {
            'username': {'required': True},
            'password':   {'write_only': True},
            
        }
    
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already in use.')
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError('The Passwords Do not match')
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return CustomUser.objects.create_user(**validated_data)

    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        data['email'] = self.user.email
        data['username'] = self.user.username
        data['id'] = self.user.id
        return data
    


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = ['user', 'followed_user']
        
class MyProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    
    art_posts = ArtSerializer(source='user.art_posts', many=True, read_only=True)
    class Meta:
        model = MyProfileModel
        fields = ['id', 'user', 'bio', 'avatar', 'created_at', 'followers_count', 'following_count', 'art_posts']
        read_only_fields = ['user', 'created_at']
        
    
    def get_followers_count(self, obj):
        return obj.user.followers.count()

    def get_following_count(self, obj):
        return obj.user.following.count()
    
    
# this class to make the search class
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username']