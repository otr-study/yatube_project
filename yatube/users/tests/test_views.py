# users/tests/test_urls.py
from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='auth',
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(UsersURLTests.user)

    def test_pages_accessible_by_name(self):
        """URLs, генерируемые по имени, доступны."""
        urls_locations = {
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:password_change_done'): HTTPStatus.OK,
            reverse('users:password_change'): HTTPStatus.OK,
            reverse('users:password_reset'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': '123', 'token': '123'}
            ): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK,
        }
        for reverse_name, expect_status in urls_locations.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(response.status_code, expect_status)

    def test_about_page_uses_correct_template(self):
        """Проверка статитечских шаблоно по имени"""
        urls_templates = {
            reverse('users:login'): 'users/login.html',
            reverse('users:signup'): 'users/signup.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            reverse('users:password_change'): 'users/password_change_form.html',
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': '123', 'token': '123'}
            ): 'users/password_reset_confirm.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for reverse_name, template in urls_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_post_context(self):
        """Контекст формы регистрации пользователя"""
        response = self.client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
