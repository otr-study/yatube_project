from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class AboutStaticTests(TestCase):
    def test_urls_exists_at_desired_location(self):
        """Проверка существования static urls."""
        urls_locations = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
        }
        for url, expect_status in urls_locations.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, expect_status)

    def test_urls_uses_correct_templates(self):
        """Проверка использования static templates."""
        urls_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)

    def test_pages_accessible_by_name(self):
        """Static URLs, генерируемые по имени, доступны."""
        urls_locations = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
        }
        for reverse_name, expect_status in urls_locations.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(response.status_code, expect_status)

    def test_about_page_uses_correct_template(self):
        """Проверка статитечских шаблоно по имени."""
        urls_templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for reverse_name, template in urls_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)
