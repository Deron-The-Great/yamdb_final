from django.urls import include, path
from rest_framework import routers

from .views import (
    register, get_token, TitleViewSet, GenreViewSet,
    CategoryViewSet, ReviewViewSet, CommentViewSet,
    UserViewSet
)

router_vol1 = routers.DefaultRouter()
router_vol1.register(r'titles', TitleViewSet, basename='titles')
router_vol1.register(r'genres', GenreViewSet, basename='genres')
router_vol1.register(r'categories', CategoryViewSet, basename='categories')
router_vol1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
)
router_vol1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments',
)
router_vol1.register(r'users', UserViewSet, basename='users')
# Регистрировать урлы здесь

auth_patterns = [
    path('signup/', register, name='register'),
    path('token/', get_token, name='get_token')
]

urlpatterns = [
    path('v1/auth/', include(auth_patterns)),
    path('v1/', include(router_vol1.urls)),
]
