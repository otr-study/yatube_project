from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.constraints import UniqueConstraint

SLUG_HELP_TEXT = (
    'Может содержать символы английского алфавита цифры и символы: "_", "-".'
)
PATH_POSTS_IMAGE = getattr(settings, 'PATH_POSTS_IMAGE', 'posts/')

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        'Содержимое поста',
        help_text='Введите текст записи'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to=PATH_POSTS_IMAGE,
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=SLUG_HELP_TEXT
    )
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Запись'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        'Комментарий'
    )
    created = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = (
            UniqueConstraint(
                fields=('user', 'author',),
                name='unique_follow'
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
