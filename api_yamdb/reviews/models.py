from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MinValueValidator, MaxValueValidator
)
from django.db import models


from reviews.validators import (
    regex_validator, me_validator, validate_year_not_in_future
)
from api_yamdb.settings import (
    BASE_FIELD_SIZE, NAME_FIELD_SIZE, SLUG_FIELD_SIZE
)


class User(AbstractUser):
    """Кастомная модель User. Дополнена полями биографии и роли."""
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    ROLES = [
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
    ]

    username = models.CharField(
        max_length=NAME_FIELD_SIZE,
        unique=True,
        validators=[regex_validator, me_validator],
        verbose_name='Ник пользователя',
    )
    email = models.EmailField(
        max_length=BASE_FIELD_SIZE,
        unique=True,
        verbose_name='Адрес электроннной почты'
    )
    first_name = models.CharField(
        max_length=NAME_FIELD_SIZE,
        blank=True,
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=NAME_FIELD_SIZE,
        blank=True,
        verbose_name='Фамилия пользователя'
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True
    )
    role = models.CharField(
        max_length=max(len(role) for role, _ in ROLES),
        choices=ROLES,
        default=USER,
        verbose_name='Роль'
    )

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER


class CategoryGenre(models.Model):
    name = models.CharField(
        max_length=BASE_FIELD_SIZE, verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=SLUG_FIELD_SIZE,
        unique=True,
        verbose_name='Краткое имя страницы',
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(CategoryGenre):
    """Описывает модель категории произведения."""

    class Meta(CategoryGenre.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryGenre):
    """Описывает модель жанра произведения."""

    class Meta(CategoryGenre.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Описывает модель произведения."""
    name = models.CharField(
        max_length=BASE_FIELD_SIZE, verbose_name='Название'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre, related_name='titles', verbose_name='Жанр'
    )
    year = models.PositiveSmallIntegerField(
        null=True,
        verbose_name='Год выпуска',
        validators=[validate_year_not_in_future]
    )
    description = models.TextField(null=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:15]


class CommentReview(models.Model):
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='%(class)ss',
        verbose_name='Автор'
    )

    class Meta:
        abstract = True
        ordering = ['pub_date']

    def __str__(self):
        return (f'{self.author.username}, {self.text[:15]}, '
                f'{self.pub_date}')


class Review(CommentReview):
    """Описывает модель отзывов"""
    score = models.PositiveIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        help_text='Введите оценку',
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Произведение'
    )

    class Meta(CommentReview.Meta):
        constraints = [models.UniqueConstraint(
            fields=['author', 'title'], name='unique_author_title'
        )]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(CommentReview):
    """Описывает модель комментариев."""
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        null=True, verbose_name='Комментируемый отзыв'
    )

    class Meta(CommentReview.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
