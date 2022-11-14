from rest_framework import serializers
from django.contrib.auth.models import User

from blog.models import Post


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class LentaSerializer(serializers.ModelSerializer):
    raise NotImplementedError
