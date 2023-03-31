from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_username, validate_year

START_YEAR = 1920
NAME_USER_LEN = 150
NAME_LEN = 256
SLUG_LEN = 50
ROLE_CHOICES = 50


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = [
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    ]

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        validators=(validate_username,),
        max_length=NAME_USER_LEN,
        null=False,
        unique=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=ROLE_CHOICES,
        choices=ROLES,
        default=USER,
    )
    bio = models.TextField(
        verbose_name='Биография',
        null=True,
        blank=True
    )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    name = models.CharField('Категория', max_length=NAME_LEN)
    slug = models.SlugField('Слаг', max_length=SLUG_LEN, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=NAME_LEN)
    slug = models.SlugField('Слаг', max_length=SLUG_LEN, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    RATING_CHOISES = [(c, str(c)) for c in range(1, 6)]

    name = models.CharField('Произведение', max_length=NAME_LEN)
    year = models.IntegerField('Год выхода', validators=[validate_year])
    description = models.TextField('Описание', blank=True, null=True)
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        through='GenreTitle'
    )
    rating = models.IntegerField(
        'Рейтинг',
        choices=RATING_CHOISES,
        null=True,
        default=None,
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        indexes = [models.Index(fields=['name', 'category'])]
        default_related_name = 'titles'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='titles'
    )
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE,
        related_name='genres'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'genre',),
                name='title_genre'
            ),
        ]
        verbose_name = 'Произведение, жанр'
        verbose_name_plural = 'Произведения, жанры'

    def __str__(self):
        return f'{self.title.name}, {self.genre.name}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(1, 'Допустимы значения от 1 до 10'),
            MaxValueValidator(10, 'Допустимы значения от 1 до 10')
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        ordering = ['pub_date']
        constraints = [
            models.UniqueConstraint(
                name='unique_author',
                fields=['author', 'title'],
            ),
        ]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ['pub_date']
