from django.test import TestCase
from .models import CustomUser, Post
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.test import RequestsClient

from .serializers import PostSerializer
from .views import UserPostsViewSet

factory = APIRequestFactory()
client = RequestsClient()
HOST = 'http://localhost:8000/'


class CustomUserTest(TestCase):

    def setUp(self):
        CustomUser.objects.create(username='User1')
        CustomUser.objects.create(username='User2')
        CustomUser.objects.create(username='User3')

    def test_user_readers(self):
        user1 = CustomUser.objects.get(username='User1')
        user2 = CustomUser.objects.get(username='User2')
        user3 = CustomUser.objects.get(username='User3')

        self.assertEqual(user1.username, 'User1')

        user1.readers.add(user2)

        self.assertEqual(user2 in user1.readers.all(), True)
        self.assertEqual(user3 in user1.readers.all(), False)


class TestLogin(TestCase):

    def setUp(self):
        CustomUser.objects.create(username='User1', password='Password1')

    def test_login_correct(self):
        response = client.get('http://localhost:8000/accounts/drf-auth/login/')
        assert response.status_code == 200
        csrftoken = response.cookies['csrftoken']

        response = client.post('http://localhost:8000/accounts/drf-auth/login/', json={
            "username": 'User1',
            "password": 'Password1'

        }, headers={'X-CSRFToken': csrftoken})
        assert response.status_code == 200


class TestPostView(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create(username='User1', password='Password1')
        self.user2 = CustomUser.objects.create(username='User2')
        self.post1 = Post.objects.create(author=self.user, title='Post Title', description='Post description')
        self.URL = f'{HOST}accounts/profile/blog/'

    def test_blog(self):
        request = factory.get(self.URL)
        force_authenticate(request, user=self.user)
        view = UserPostsViewSet.as_view({'get': 'list'})
        response = view(request)
        assert response.status_code == 200

    def test_post_check(self):
        request = factory.get(self.URL)
        force_authenticate(request, user=self.user)
        view = UserPostsViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=self.post1.id)
        self.assertEqual(response.data, PostSerializer(self.post1).data)
        response = view(request, pk=1000)
        self.assertEqual(response.status_code, 404)

    def test_post_create(self):
        request = factory.post(self.URL, {'title': 'titlepost',
                                          'description': 'description'},
                               format='json')
        force_authenticate(request, user=self.user)
        view = UserPostsViewSet.as_view({'post': 'create'})

        response = view(request)
        post = Post.objects.get(title='titlepost')
        self.assertEqual(response.data, PostSerializer(post).data)

    def test_post_delete(self):
        request = factory.delete(self.URL,
                                 {'id': self.post1.id}, format='json')

        force_authenticate(request, user=self.user)

        view = UserPostsViewSet.as_view({'delete': 'delete'})

        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_noexist_post_delete(self):
        request = factory.delete(self.URL,
                                 {'id': 100}, format='json')

        force_authenticate(request, user=self.user)

        view = UserPostsViewSet.as_view({'delete': 'delete'})

        response = view(request)
        self.assertEqual(response.status_code, 404)

    def test_alien_post_delete(self):
        request = factory.delete(self.URL, {'id': self.post1.id}, format='json')
        force_authenticate(request, user=self.user2)
        view = UserPostsViewSet.as_view({'delete': 'delete'})
        response = view(request)
        self.assertEqual(response.status_code, 403)
