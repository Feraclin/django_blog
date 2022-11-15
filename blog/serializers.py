from rest_framework import serializers

from .models import Post, CustomUser, Feed


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username')


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = ('id', 'author', 'title', 'description')


class UserPostsSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'posts']


class UserSubscriptionsSerializer(serializers.ModelSerializer):
    readers = UserSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'readers']


class FeedSerializer(serializers.ModelSerializer):
    title = serializers.ReadOnlyField(source='post.title')
    text = serializers.ReadOnlyField(source='post.description')
    publish_date = serializers.ReadOnlyField(source='post.publish_date')

    class Meta:
        model = Feed
        fields = ('id', 'title', 'text', 'publish_date', 'post_readed')

