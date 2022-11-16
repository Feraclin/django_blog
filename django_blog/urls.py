"""django_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from blog.routers import router_blog
from blog.views import UserListView, PostsView, UserSubscriptionsViewSet, SubscriptionView, ProfileView, \
    RebuildFeedView, index
from .settings import DEBUG

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/drf-auth/', include('rest_framework.urls')),
    path('accounts/profile/', ProfileView.as_view()),
    path('accounts/profile/', include(router_blog.urls)),
    path('api/v1/users', UserListView.as_view()),
    path('api/v1/posts/', PostsView.as_view(), name='user-post'),
    path('api/v1/subscription', UserSubscriptionsViewSet.as_view()),
    path('api/v1/subscription/<int:pk>', SubscriptionView.as_view()),
    path('rebuildfeed/', RebuildFeedView.as_view()),
    path('send_email/', index),

]

if DEBUG:
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))
