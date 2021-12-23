from http import HTTPStatus

from .test_utils import PostTestCase, User


class PostURLTests(PostTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_not_author = User.objects.create_user(username='not_author')

    def test_urls_exists_at_desired_location(self):
        """Доступность страниц любому пользователю."""
        urls_locations = {
            '/': HTTPStatus.OK,
            '/group/empty_group/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            '/create/': HTTPStatus.FOUND,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/non_existent': HTTPStatus.NOT_FOUND,
        }
        for url, expect_status in urls_locations.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, expect_status)

    def test_authorized_urls_exists_at_desired_location(self):
        """Доступность страниц авторизованному пользователю."""
        self.client.force_login(self.user)
        urls_locations = {
            '/create/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.OK,
        }
        for url, expect_status in urls_locations.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, expect_status)

    def test_urls_created_available_not_author(self):
        """Доступность страницы created не автору."""
        self.client.force_login(self.user_not_author)
        response = self.client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_templates(self):
        """Проверка связанности путей с шаблонами."""
        self.client.force_login(self.user)
        urls_templates = {
            '/': 'posts/index.html',
            '/group/empty_group/': 'posts/group_list.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect_anonymous(self):
        """Проверка редиректов анонимуса."""
        url_edit = f'/posts/{self.post.id}/edit/'
        urls_redirect_urls = {
            '/create/': '/auth/login/?next=/create/',
            url_edit: f'/auth/login/?next={url_edit}',
        }
        for url, redirect_url in urls_redirect_urls.items():
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)
                self.assertRedirects(
                    response, (redirect_url))

    def test_url_edit_redirect_not_author(self):
        """Проверка редиректа редактирования поста."""
        self.client.force_login(self.user_not_author)
        url = f'/posts/{self.post.id}/edit/'
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, f'/posts/{self.post.id}/')
