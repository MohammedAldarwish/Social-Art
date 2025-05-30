from rest_framework import serializers 
from .models import ArtModel, ArtImage, Comment, ArtLike


class ArtImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtImage
        fields = ['image']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['user', 'content', 'created_at']
        
        
class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ArtLike
        fields = ['user', 'created_at']
        


class ArtSerializer(serializers.ModelSerializer):
    images = ArtImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    
    def get_like_count(self, obj):
        return obj.likes.count()
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    
        
    
    class Meta:
        model = ArtModel
        fields = [
            'user', 'title', 'description',
            'categories', 'posted_at', 'images',
            'comments', 'likes',
            'like_count', 'comment_count'
            ]
        read_only_fields = ['user', 'posted_at', 'like_count', 'comment_count']
 


class CreateCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Comment
        fields = ['user','art_post', 'content']



class CreateLikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = ArtLike
        fields = ['user', 'art_post', 'created_at']
