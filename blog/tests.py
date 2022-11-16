
from django.test import TestCase
from .models import CustomUser, Post
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.test import RequestsClient

from .serializers import PostSerializer
from .service import post_editor
from .tasks import send_feed
from .views import UserPostsViewSet, SubscriptionView, FeedViewSet

factory = APIRequestFactory()
client = RequestsClient()
HOST = 'http://localhost:8000/'


class CustomUserTest(TestCase):

    def setUp(self):
        self.user1 = CustomUser.objects.create(username='User1')
        self.user2 = CustomUser.objects.create(username='User2')
        self.user3 = CustomUser.objects.create(username='User3')

    def test_user_readers(self):
        self.assertEqual(self.user1.username, 'User1')

        self.user1.readers.add(self.user2)

        self.assertEqual(self.user2 in self.user1.readers.all(), True)
        self.assertEqual(self.user3 in self.user1.readers.all(), False)


class TestLogin(TestCase):

    def setUp(self):
        CustomUser.objects.create(username='User1', password='Password1')
        self.URL = f'{HOST}accounts/drf-auth/login/'

    def test_login_correct(self):
        response = client.get(self.URL)
        assert response.status_code == 200
        csrftoken = response.cookies['csrftoken']

        response = client.post(self.URL, json={
            "username": 'User1',
            "password": 'Password1'

        }, headers={'X-CSRFToken': csrftoken})
        assert response.status_code == 200


class TestPostView(TestCase):

    def setUp(self):
        self.user1 = CustomUser.objects.create(username='User1', password='Password1')
        self.user2 = CustomUser.objects.create(username='User2')
        self.post1 = Post.objects.create(author=self.user1, title='Post Title', description='Post description')
        self.user1.readers.add(self.user2)
        self.URL = f'{HOST}accounts/profile/blog/'

    def test_blog(self):
        request = factory.get(self.URL)
        force_authenticate(request, user=self.user1)
        view = UserPostsViewSet.as_view({'get': 'list'})
        response = view(request)
        assert response.status_code == 200

    def test_post_check(self):
        request = factory.get(self.URL)
        force_authenticate(request, user=self.user1)
        view = UserPostsViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=self.post1.id)
        self.assertEqual(response.data, PostSerializer(self.post1).data)
        response = view(request, pk=1000)
        self.assertEqual(response.status_code, 404)

    def test_post_create_and_feed(self):
        request = factory.post(self.URL, {'title': 'titlepost',
                                          'description': 'description'},
                               format='json')
        force_authenticate(request, user=self.user1)
        view = UserPostsViewSet.as_view({'post': 'create'})

        response = view(request)
        response.render()
        post = Post.objects.get(title='titlepost')
        post_editor.create_post(users_lst=self.user1.readers.iterator(),
                                post=post)

        self.assertEqual(response.data, PostSerializer(post).data)

        request = factory.get(self.URL.replace('blog', 'feed'))
        force_authenticate(request, user=self.user2)
        view = FeedViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.data['results'][0]['title'], post.title)
        send_feed()

    def test_post_delete(self):
        request = factory.delete(self.URL,
                                 {'id': self.post1.id}, format='json')

        force_authenticate(request, user=self.user1)

        view = UserPostsViewSet.as_view({'delete': 'delete'})

        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_noexist_post_delete(self):
        request = factory.delete(self.URL,
                                 {'id': 100}, format='json')

        force_authenticate(request, user=self.user1)

        view = UserPostsViewSet.as_view({'delete': 'delete'})

        response = view(request)
        self.assertEqual(response.status_code, 404)

    def test_alien_post_delete(self):
        request = factory.delete(self.URL, {'id': self.post1.id}, format='json')
        force_authenticate(request, user=self.user2)
        view = UserPostsViewSet.as_view({'delete': 'delete'})
        response = view(request)
        self.assertEqual(response.status_code, 403)


class TestSubscribersView(TestCase):

    def setUp(self):
        self.user1 = CustomUser.objects.create(username='User1')
        self.user2 = CustomUser.objects.create(username='User2')
        self.user3 = CustomUser.objects.create(username='User3')
        self.user3.readers.add(self.user1)
        self.URL = f'{HOST}api/v1/subscription/'

    def test_self_subscription(self):
        request = factory.post(self.URL)
        force_authenticate(request, user=self.user1)
        view = SubscriptionView.as_view()
        response = view(request, pk=self.user1.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, 'Your are not subscribe yourself')

    def test_new_subscription(self):
        request = factory.post(self.URL)
        force_authenticate(request, user=self.user1)
        view = SubscriptionView.as_view()
        self.assertEqual(self.user1 in self.user2.readers.all(), False)
        response = view(request, pk=self.user2.id)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user1 in self.user2.readers.all(), True)

    def test_noexist_subscription(self):
        request = factory.post(self.URL)
        force_authenticate(request, user=self.user1)
        view = SubscriptionView.as_view()
        response = view(request, pk=50)
        self.assertEqual(response.status_code, 404)

    def test_delete_subscription(self):
        request = factory.delete(self.URL)
        force_authenticate(request, user=self.user1)
        view = SubscriptionView.as_view()
        response = view(request, pk=self.user3.id)
        self.assertEqual(response.status_code, 204)

    def test_delete_noexist_subscription(self):
        request = factory.delete(self.URL)
        force_authenticate(request, user=self.user1)
        view = SubscriptionView.as_view()
        response = view(request, pk=50)
        self.assertEqual(response.status_code, 404)

    def test_delete_unsubscription(self):
        request = factory.delete(self.URL)
        force_authenticate(request, user=self.user1)
        view = SubscriptionView.as_view()
        response = view(request, pk=self.user2.id)
        self.assertEqual(response.status_code, 404)

