from rest_framework import routers

from blog.views import UserPostsViewSet

router_blog = routers.SimpleRouter()

router_blog.register(r'blog', UserPostsViewSet, basename='blog')
