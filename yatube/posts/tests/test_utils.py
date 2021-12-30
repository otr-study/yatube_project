import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from ..models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        image = cls.create_img()
        cls.user = cls.create_user()
        cls.group = cls.create_group()
        cls.post = cls.create_post(image=image)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def create_post(cls, **kwargs):
        group = None
        if not kwargs.get('empty_group'):
            group = kwargs.get('group') or cls.group
        user = kwargs.get('user') or cls.user
        postfix = kwargs.get('postfix') or ''
        image = kwargs.get('image') or None
        return Post.objects.create(
            author=user,
            text=f'Текст большого-пребольшого тестового поста {postfix}',
            group=group,
            image=image,
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

    @classmethod
    def create_img(cls, **kwargs):
        filename = kwargs.get('filename') or 'small.gif'
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        return SimpleUploadedFile(
            name=filename,
            content=small_gif,
            content_type='image/gif'
        )

    @classmethod
    def create_comment(cls, **kwargs):
        post = kwargs.get('post') or cls.post
        user = kwargs.get('user') or cls.user
        postfix = kwargs.get('postfix') or ''
        return Comment.objects.create(
            post=post,
            author=user,
            text=f'Текст большого-пребольшого тестового комментария {postfix}'
        )
