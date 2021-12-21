# posts/tests/test_forms.py
from core.test_utils import PostTestCase
from django.test import Client
from django.urls import reverse
from posts.views import Post


class PostFormTests(PostTestCase):
    def setUp(self):
        self.client = Client()
        self.client.force_login(PostFormTests.user)

    def test_create_valid_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Запись добавленная при тестировании формы',
            'group': PostFormTests.group.id,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(PostFormTests.user.username,))
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Запись добавленная при тестировании формы',
                group=PostFormTests.group
            ).exists()
        )

    def test_create_invalid_post(self):
        """Невалидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': '',
            'group': PostFormTests.group.id,
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
        form_data = {
            'text': 'Запись измененная при тестировании формы',
            'group': PostFormTests.group.id,
        }
        response = self.client.post(
            reverse('posts:post_edit', args=(PostFormTests.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(PostFormTests.post.id,))
        )
        self.assertTrue(
            Post.objects.filter(
                text='Запись измененная при тестировании формы',
                group=PostFormTests.group
            ).exists()
        )
