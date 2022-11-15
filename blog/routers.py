from rest_framework import routers

from blog.views import UserPostsViewSet, FeedViewSet

router_blog = routers.SimpleRouter()

router_blog.register(r'blog', UserPostsViewSet, basename='blog')
router_blog.register(r'feed', FeedViewSet, basename='feed')
