from rest_framework import generics, mixins, viewsets, permissions, views, response

from .models import CustomUser
from .serializers import UserSerializer, UserPostsSerializer, UserSubscriptionsSerializer


class UserListView(generics.ListAPIView):
    '''Вывод списка пользователей
    '''
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UsersPostsVIew(generics.ListAPIView):
    ''' Вывод списка постов
    '''
    queryset = CustomUser.objects.all()
    serializer_class = UserPostsSerializer


class UserPostsViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    '''Вывод списка постов полтзователя
    '''
    queryset = CustomUser.objects.all()
    serializer_class = UserPostsSerializer


class UserSubscriptionsViewSet(generics.ListAPIView):
    """ Вывод списка подписок
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
        user.readers.add(author)
        return response.Response(status=201)

    def delete(self, request, pk):
        try:
            author = CustomUser.objects.get(id=pk)
        except CustomUser.DoesNotExist:
            return response.Response(status=404)
        user = CustomUser.objects.get(username=self.request.user)
        user.readers.remove(author)
        return response.Response(status=204)
