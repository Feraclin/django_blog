from pprint import pprint

from django.test import TestCase
from .models import CustomUser, Post
from rest_framework.test import APIRequestFactory, force_authenticate
from requests.auth import HTTPBasicAuth
from rest_framework.test import RequestsClient

from .views import UserPostsViewSet

factory = APIRequestFactory()
client = RequestsClient()



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
        user = CustomUser.objects.create(username='User1', password='Password1')
        post = Post.objects.create(author=user, title='Post Title', description='Post description')

    def test_blog(self):
        user1 = CustomUser.objects.get(username='User1')
        request = factory.get('http://localhost:8080/accounts/profile/blog/')
        force_authenticate(request, user=user1)
        view = UserPostsViewSet.as_view({'get': 'list'})
        response = view(request)
        assert response.status_code == 200

    def test_post_check(self):
        user1 = CustomUser.objects.get(username='User1')
        post = Post.objects.get(title='Post Title')
        request = factory.get(f'http://localhost:8080/accounts/profile/blog/')
        force_authenticate(request, user=user1)
        view = UserPostsViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=post.id)
        assert response.status_code == 200
        response = view(request, pk=1000)
        assert response.status_code == 404

    def test_post_create(self):
        user1 = CustomUser.objects.get(username='User1')
        request = factory.post(f'http://localhost:8080/accounts/profile/blog/')
        force_authenticate(request, user=user1)
        view = UserPostsViewSet.as_view({'post': 'update'})
        response = view(request, pk=None)
        print(response)