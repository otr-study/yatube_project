from django.conf import settings
from django.test import Client
from django.urls import reverse

from ..views import Post
from .test_utils import PostTestCase

PATH_POSTS_IMAGE = getattr(settings, 'PATH_POSTS_IMAGE', 'posts/')


class PostFormTests(PostTestCase):
    def setUp(self):
        self.client.force_login(self.user)
        self.non_authorized_client = Client()

    def test_create_valid_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        img_name = 'tst_create.gif'
        form_data = {
            'text': 'Запись добавленная при тестировании формы',
            'group': self.group.id,
            'image': self.create_img(filename=img_name),
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user.username,))
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image=f'{PATH_POSTS_IMAGE}{img_name}',
            ).exists(),
            'Ошибка проверки полей нового поста.'
        )

    def test_create_invalid_post(self):
        """Невалидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': '',
            'group': self.group.id,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFormError(
            response,
            'form',
            'text',
            'Обязательное поле.'
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):
        """Форма редактирует запись в Post."""
        img_name = 'tst_edit.gif'
        form_data = {
            'text': 'Запись измененная при тестировании формы',
            'group': self.group.id,
            'image': self.create_img(filename=img_name),
        }
        response = self.client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, form_data['text'])
        self.assertEqual(self.post.group.id, form_data['group'])
        self.assertEqual(
            self.post.image,
            f'{PATH_POSTS_IMAGE}{img_name}',
            'Ошибка проверки изменения изображения.'
        )

    def test_anonymous_create_post(self):
        """Анонимный пользователь не может создать пост."""
        form_data = {
            'text': 'Анонимный пользователь создал этот пост',
            'group': self.group.id,
        }
        response = self.non_authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=/create/'
        )

    def test_anonymous_edit_post(self):
        """Анонимный пользователь не может редактировать пост."""
        form_data = {
            'text': 'Анонимный пользователь отредактировал этот пост',
            'group': self.group.id,
        }
        response = self.non_authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        url_edit = f'/posts/{self.post.id}/edit/'
        self.assertRedirects(
            response,
            reverse('users:login') + f'?next={url_edit}'
        )
