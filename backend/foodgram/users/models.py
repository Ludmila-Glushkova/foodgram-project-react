from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        validators=(UnicodeUsernameValidator(),),
        help_text='Необходимо указать логин'
    )
    email = models.EmailField(
        'Почта',
        max_length=254,
        unique=True,
        help_text='Необходимо указать электронную почту'
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        help_text='Необходимо указать имя'
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        help_text='Необходимо указать фамилию'
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
        help_text='Необходимо указать пароль'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='Нельзя подписаться на свой аккаунт'
            ),
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='Нельзя повторно подписаться на пользователя'
            )
        ]
        verbose_name = 'Подписка',
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
