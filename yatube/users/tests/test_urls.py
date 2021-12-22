import re
from http import HTTPStatus

from django.contrib.auth import authenticate, get_user_model
from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings

User = get_user_model()

USR_PASSWD = '123'
NEW_USR_PASSWD = '321sdfa3('
NEW_USR_PASSWD2 = '241sxd3-fa4'
USER_NAME = 'auth'
USR_EMAIL = 'tst@tst.com'


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=USER_NAME,
            password=USR_PASSWD,
            email=USR_EMAIL,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_urls_exists_at_desired_location(self):
        """Доступность страниц авторизованному пользователю."""
        urls_locations = {
            '/auth/login/': HTTPStatus.OK,
            '/auth/signup/': HTTPStatus.OK,
            '/auth/password_change/done/': HTTPStatus.OK,
            '/auth/password_change/': HTTPStatus.OK,
            '/auth/password_reset/': HTTPStatus.OK,
            '/auth/password_reset/done/': HTTPStatus.OK,
            '/auth/reset/done/': HTTPStatus.OK,
            '/auth/reset/123/123/': HTTPStatus.OK,
            '/auth/logout/': HTTPStatus.OK,
        }
        for url, expect_status in urls_locations.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, expect_status)

    def test_urls_uses_correct_templates(self):
        """Проверка связанности путей с шаблонами."""
        urls_templates = {
            '/auth/login/': 'users/login.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/reset/123/123/': 'users/password_reset_confirm.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)

    def test_change_password(self):
        """Проверка изменения пароля."""
        response = self.client.post(
            '/auth/password_change/',
            data={
                'old_password': USR_PASSWD,
                'new_password1': NEW_USR_PASSWD,
                'new_password2': NEW_USR_PASSWD,
            },
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/password_change_done.html')
        self.assertIsNotNone(
            authenticate(username=USER_NAME, password=NEW_USR_PASSWD)
        )

    def test_reset_password(self):
        """Проверка сброса пароля."""
        if self.user.is_authenticated:
            self.client.logout()
        response = self.client.post(
            '/auth/password_reset/',
            {"email": USR_EMAIL},
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        uidb64, token = self.utils_extract_reset_tokens(msg.body)
        response = self.client.get(
            f'/auth/reset/{uidb64}/{token}/',
            follow=True
        )
        url = f'/auth/reset/{uidb64}/set-password/'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, url)

        response = self.client.post(
            url,
            data={
                'new_password1': NEW_USR_PASSWD2,
                'new_password2': NEW_USR_PASSWD2
            },
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/password_reset_complete.html')
        self.assertIsNotNone(
            authenticate(username=USER_NAME, password=NEW_USR_PASSWD2)
        )

    def utils_extract_reset_tokens(self, full_url):
        return re.findall(
            r'/([\w\-]+)',
            re.search(r'^http\://.+$', full_url, flags=re.MULTILINE)[0]
        )[3:5]
