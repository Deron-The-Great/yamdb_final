from django.db import IntegrityError
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from .permissions import (
    IsAdminOrReadOnly, IsAdminModeratorAuthorOrReadOnly, AdminOnly
)
from .serializers import (
    RegisterDataSerializer, TokenSerializer, GenreSerializer,
    CategorySerializer, TitleBaseSerializer, TitleAddSerializer,
    CommentSerializer, ReviewSerializer, UserSerializer,
    UserEditSerializer
)
from api_yamdb.settings import DEFAULT_MAILING_ADDRESS
from reviews.models import User, Category, Genre, Title, Comment, Review


def send_email(user):
    send_mail(
        subject='YaMDb registration',
        message=(
            f'Your confirmation code: '
            f'{default_token_generator.make_token(user)}'
        ),
        from_email=DEFAULT_MAILING_ADDRESS,
        recipient_list=[user.email],
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterDataSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user, _ = User.objects.get_or_create(
            email=serializer.validated_data['email'],
            username=serializer.validated_data['username']
        )
    except IntegrityError:
        return Response(
            'This username or email already exists',
            status=status.HTTP_400_BAD_REQUEST
        )
    send_email(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )

    if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
    ):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryGenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [
        IsAdminOrReadOnly,
    ]
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(CategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly, ]
    ordering = ['name']

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleBaseSerializer
        return TitleAddSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        return self.get_review().comments.all()


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAdminModeratorAuthorOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly
    )

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserEditSerializer,
    )
    def user_own_profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
        else:
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
