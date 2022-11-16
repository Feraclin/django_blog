from django.http import HttpResponse
from rest_framework import generics, mixins, viewsets, permissions, views, response

from .models import CustomUser, Post, Feed
from .pagination import APIListPagination
from .serializers import UserSerializer, \
                        UserSubscriptionsSerializer, \
                        PostSerializer, \
                        UserPostsSerializer, \
                        FeedSerializer
from .service import post_editor
from .tasks import send_feed, creater_feed


def index(request):
    send_feed.delay()
    return HttpResponse('Send!')


class UserListView(generics.ListAPIView):
    '''Вывод списка пользователей
    '''
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class PostsView(generics.ListAPIView):
    ''' Вывод списка постов
    '''
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = APIListPagination


class ProfileView(generics.ListAPIView):
    '''Просмотр профиля
    '''
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserPostsSerializer
    pagination_class = APIListPagination

    def get_queryset(self):
        return CustomUser.objects.filter(username=self.request.user)


class FeedViewSet(mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    '''Лента постов
    '''
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FeedSerializer
    pagination_class = APIListPagination

    def get_queryset(self):
        # TODO: Переделать сортировку, сейчас костыль
        # TODO: Добавить кеширование
        return Feed.objects.filter(recipient=self.request.user).select_related('post').order_by('-post_id')[:500]


class UserPostsViewSet(
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    '''Управление постами пользователя
    '''
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer
    pagination_class = APIListPagination

    def get_queryset(self):
        author = CustomUser.objects.get(username=self.request.user)
        return Post.objects.filter(author=author).select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def post(self, request):
        author = CustomUser.objects.get(username=self.request.user)
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(author=author)
        # creater_feed.delay(users_lst=author.readers.iterator(),
        #                    post=post)
        post_editor.create_post(users_lst=author.readers.iterator(),
                                post=post)
        return response.Response(serializer.data, status=201)

    def delete(self, request):
        author = CustomUser.objects.get(username=self.request.user)
        post = Post.objects.get(id=request.data['id'])
        if post.author == author:
            post.delete()
            return response.Response(status=200)
        else:
            return response.Response(status=403)


class UserSubscriptionsViewSet(generics.ListAPIView):
    """ Вывод списка подписчиков
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSubscriptionsSerializer
    pagination_class = APIListPagination

    def get_queryset(self):
        return CustomUser.objects.filter(username=self.request.user)


class SubscriptionView(views.APIView):
    '''Управление подпиской
    '''

    def post(self, request, pk):
        user = CustomUser.objects.get(username=self.request.user)
        if user.id == pk:
            return response.Response(status=403, data="Your are not subscribe yourself")
        try:
            author = CustomUser.objects.get(id=pk)
        except CustomUser.DoesNotExist:
            return response.Response(status=404)
        author.readers.add(user)
        return response.Response(status=201)

    def delete(self, request, pk):
        try:
            author = CustomUser.objects.get(id=pk)
        except CustomUser.DoesNotExist:
            return response.Response(status=404)
        user = CustomUser.objects.get(username=self.request.user)
        if user in author.readers:
            author.readers.remove(user)
            return response.Response(status=204)
        else:
            return response.Response(status=404)


class RebuildFeedView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @staticmethod
    def get(request):
        return response.Response('Rebuild all feed')

    @staticmethod
    def post(request):
        # Временноe решение для перестроения ленты
        all_posts = Post.objects.iterator()
        for i in all_posts:
            post_editor.create_post(users_lst=i.author.readers.all(),
                                    post=i)
        return response.Response(status=200)
