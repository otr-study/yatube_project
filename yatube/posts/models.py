from django.contrib.auth import get_user_model
from django.db import models

SLUG_HELP_TEXT = (
    'Может содержать символы английского алфавита цифры и символы: "_", "-".'
)

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

    class Meta:
        ordering = ('-pub_date',)

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

    def __str__(self):
        return self.title
