from rest_framework import generics, mixins, viewsets, permissions, views, response

from .models import CustomUser, Post, Feed
from .pagination import PostsAPIListPagination
from .serializers import UserSerializer, \
                        UserSubscriptionsSerializer, \
                        PostSerializer, \
                        UserPostsSerializer, \
                        FeedSerializer
from .service import post_editor


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
    pagination_class = PostsAPIListPagination


class ProfileView(generics.ListAPIView):
    '''Просмотр профиля
    '''
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserPostsSerializer
    pagination_class = PostsAPIListPagination

    def get_queryset(self):
        return CustomUser.objects.filter(username=self.request.user)


class FeedViewSet(mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    '''Лента постов
    '''
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FeedSerializer
    pagination_class = PostsAPIListPagination

    def get_queryset(self):
        # TODO: Переделать сортировку, сейчас костыль
        # TODO: Добавить кеширование
        return Feed.objects.filter(recipient=self.request.user).select_related('post').order_by('-post_id')


class UserPostsViewSet(
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    '''Управление постами пользователя
    '''
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer

    def get_queryset(self):
        author = CustomUser.objects.get(username=self.request.user)
        return Post.objects.filter(author=author)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def post(self, request):
        author = CustomUser.objects.get(username=self.request.user)
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(author=author)
        post_editor.create_post(users_lst=author.readers.all(),
                                post=post)

        return response.Response(serializer.data, status=201)

    def delete(self, request):
        author = CustomUser.objects.get(username=self.request.user)
        post = Post.objects.get(id=request.data['id'])
        post.delete()
        return response.Response(status=200)


class UserSubscriptionsViewSet(generics.ListAPIView):
    """ Вывод списка подписчиков
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSubscriptionsSerializer

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
        author.readers.remove(user)
        return response.Response(status=204)


class RebuildFeedView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    @staticmethod
    def get(request):
        return response.Response('Rebuild all feed')

    @staticmethod
    def post(request):
        # Временно решение для перестроения ленты
        all_posts = Post.objects.all()
        for i in all_posts:
            post_editor.create_post(users_lst=i.author.readers.all(),
                                    post=i)
        return response.Response(status=200)
