from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.create_user()
        cls.group = cls.create_group()
        cls.post = cls.create_post()

    @classmethod
    def create_post(cls, **kwargs):
        group = None
        if not kwargs.get('empty_group'):
            group = kwargs.get('group') or cls.group
        user = kwargs.get('user') or cls.user
        postfix = kwargs.get('postfix') or ''
        return Post.objects.create(
            author=user,
            text=f'Текст большого-пребольшого тестового поста {postfix}',
            group=group,
        )

    @classmethod
    def create_group(cls, **kwargs):
        title = kwargs.get('title') or 'Тестовая группа'
        slug = kwargs.get('slug') or 'tst_slug'
        description = kwargs.get('description') or 'Тестовое описание'
        return Group.objects.create(
            title=title,
            slug=slug,
            description=description,
        )

    @classmethod
    def create_user(cls, **kwargs):
        username = kwargs.get('username') or 'auth'
        return User.objects.create_user(username=username)
