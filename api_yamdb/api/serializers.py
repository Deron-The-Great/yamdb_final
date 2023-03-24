from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from django.core.validators import (
    MinValueValidator, MaxValueValidator,
)

from api_yamdb.settings import BASE_FIELD_SIZE, NAME_FIELD_SIZE
from reviews.validators import (
    regex_validator, me_validator, validate_year_not_in_future
)
from reviews.models import User, Category, Genre, Title, Comment, Review


class RegisterDataSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=NAME_FIELD_SIZE,
        required=True,
        validators=[regex_validator, me_validator]
    )
    email = serializers.EmailField(max_length=BASE_FIELD_SIZE, required=True)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=NAME_FIELD_SIZE,
        required=True,
        validators=[
            regex_validator,
            me_validator
        ]
    )
    confirmation_code = serializers.CharField(required=True)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleBaseSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        read_only_fields = fields
        model = Title


class TitleAddSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, value):
        validate_year_not_in_future(value)
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    score = serializers.IntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        )
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        request = self.context['request']
        if request.method != 'POST':
            return data
        if Review.objects.filter(
            title=get_object_or_404(
                Title, pk=request.parser_context['kwargs'].get('title_id')
            ), author=request.user
        ).exists():
            raise serializers.ValidationError(
                {'error': 'Нельзя оставить повторный обзор на одну запись'})
        return data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        model = User

    def validate_username(self, value):
        regex_validator(value)
        me_validator(value)
        return value


class UserEditSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)
