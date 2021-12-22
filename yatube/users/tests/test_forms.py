from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UsersFormsTests(TestCase):
    def test_create_user(self):
        """Форма создает нового пользователя."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'new_user',
            'email': 'tst@tst.com',
            'password1': 'sdf23dk0)',
            'password2': 'sdf23dk0)',
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:index')
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='new_user'
            ).exists()
        )
