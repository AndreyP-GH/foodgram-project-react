from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


LEN_LIMIT = 15


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        max_length=150)
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150)
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150)
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        max_length=254)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:LEN_LIMIT]


class Follow(models.Model):
    """Модель подписки на авторов."""

    user = models.ForeignKey(
        User,
        verbose_name='Кто подписался',
        on_delete=models.CASCADE,
        related_name='follower',)
    author = models.ForeignKey(
        User,
        verbose_name='На кого подписался',
        on_delete=models.CASCADE,
        related_name='following',)

    class Meta:
        ordering = ('author',)
        verbose_name = 'Подписка пользователя'
        verbose_name_plural = 'Подписки пользователя'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'),
        ]

    def clean(self):
        if self.user.id == self.author.id:
            raise ValidationError('Подписка на самого себя запрещена.')

    def __str__(self):
        return f'{self.user.username}: подписки пользователя'[:LEN_LIMIT]
