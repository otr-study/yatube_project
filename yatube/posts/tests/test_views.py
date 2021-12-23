from django.core.paginator import Page
from django.test import TestCase
from django.urls import reverse

"""Екатерина, если я правильно понимаю нижеследующий импорт должен быть
отделен от предыдущего пустой строкой, но isort не дает этого сделать, он
автоматически сдвигает этот импорт вплотную к предыдущему."""
from yatube.settings import POSTS_PER_PAGE

from ..forms import PostForm
from ..models import Group, Post, User
from .test_utils import PostTestCase


class PostViewTests(PostTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.another_group = cls.create_group(
            title='Другая тестовая группа',
            slug='another_tst_slug'
        )
        cls.another_user = cls.create_user(username='another_user')
        cls.post_another_user = cls.create_post(user=cls.another_user)
        cls.post_another_group = cls.create_post(group=cls.another_group)
        cls.post_without_group = cls.create_post(empty_group=True)

    def setUp(self):
        self.client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:posts_without_group'): 'posts/group_list.html',
            reverse(
                'posts:group_list',
                args=(self.group.slug,)
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                args=(self.user.username,)
            ): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                args=(self.post.id,)
            ): 'posts/create_post.html',
            reverse(
                'posts:post_detail',
                args=(self.post.id,)
            ): 'posts/post_detail.html',
        }
        for reverse_name, template in pages_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_list_page(self):
        """Контекст списков."""
        urls_posts = [
            (reverse('posts:index'), self.post),
            (reverse('posts:group_list', args=(self.group.slug,)), self.post),
            (reverse('posts:profile', args=(self.user.username,)), self.post),
            (reverse('posts:posts_without_group'), self.post_without_group),
        ]
        for url, post_standart in urls_posts:
            with self.subTest(url=url):
                response = self.client.get(url)
                page_obj = response.context.get('page_obj')
                self.assertIsInstance(page_obj, Page)
                post = page_obj[len(page_obj) - 1]
                self.check_post_context(post, post_standart)

    def test_post_detail_context(self):
        """Контекст страницы post_detail."""
        response = self.client.get(
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.check_post_context(response.context.get('post'), self.post)

    def test_create_post_context(self):
        """Контекст формы добавления поста."""
        response = self.client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertIsNone(response.context.get('is_edit'))

    def test_edit_post_context(self):
        """Контекст формы едактирования поста."""
        response = self.client.get(
            reverse('posts:post_edit', args=(self.post.id,))
        )
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertTrue(response.context.get('is_edit'))

    def test_correct_entry_post_in_list(self):
        """Пост попадает в отведенный для него список."""
        preset = {
            reverse('posts:index'): [
                (
                    lambda x: self.post in x,
                    'Пост выводится на главной странице.',
                ),
                (
                    lambda x: self.post_another_group in x,
                    'Пост с другой группой выводится на главной странице.',
                ),
                (
                    lambda x: self.post_another_user in x,
                    'Пост другого пользователя выводится на главной странице.',
                ),
                (
                    lambda x: self.post_without_group in x,
                    'Пост без группы выводится на главной странице.'
                )
            ],
            reverse('posts:group_list', args=(self.group.slug,)): [
                (
                    lambda x: self.post in x,
                    'Пост выводится на странице группы.',
                ),
                (
                    lambda x: self.post_another_group not in x,
                    'Пост с другой группой не выводится на страницу группы.',
                ),
                (
                    lambda x: self.post_another_user in x,
                    'Пост другого пользователя выводится на страницу группы.',
                ),
                (
                    lambda x: self.post_without_group not in x,
                    'Пост без группы не выводится на страницу группы.'
                )
            ],
            reverse('posts:profile', args=(self.user.username,)): [
                (
                    lambda x: self.post in x,
                    'Пост выводится на странице профайл.',
                ),
                (
                    lambda x: self.post_another_group in x,
                    'Пост с другой группой выводится на страницу профайл.',
                ),
                (
                    lambda x: self.post_another_user not in x,
                    ('Пост другого пользователя не '
                     'выводится на страницу профайл.'),
                ),
                (
                    lambda x: self.post_without_group in x,
                    'Пост без группы не выводится на страницу профайл.'
                )
            ],
            reverse('posts:posts_without_group'): [
                (
                    lambda x: self.post not in x,
                    'Пост не выводится на странице без группы.',
                ),
                (
                    lambda x: self.post_another_group not in x,
                    ('Пост с другой группой не '
                     'выводится на страницу без группы.'),
                ),
                (
                    lambda x: self.post_another_user not in x,
                    ('Пост другого пользователя не '
                     'выводится на страницу без группы.'),
                ),
                (
                    lambda x: self.post_without_group in x,
                    'Пост без группы выводится на страницу без группы.'
                )
            ],
        }
        for url, checks in preset.items():
            for func, description in checks:
                with self.subTest(url=url, description=description):
                    response = self.client.get(url)
                    self.assertTrue(func(response.context.get('page_obj')))

    def check_post_context(self, post, post_standard):
        self.assertIsInstance(post, Post)
        self.assertEqual(post.text, post_standard.text)
        self.assertEqual(post.group, post_standard.group)
        self.assertEqual(post.author, post_standard.author)


class PostPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='test group',
            slug='slug',
            description='description',
        )
        cls.SECOND_PAGE_COUNT = 3

    def setUp(self):
        self.client.force_login(self.user)

    def test_paginator_group_urls(self):
        """Пагинатор списков."""
        posts = [
            Post(
                text=f'test post {i}',
                author=self.user,
                group=self.group,
            ) for i in range(POSTS_PER_PAGE + self.SECOND_PAGE_COUNT)
        ]
        Post.objects.bulk_create(posts)

        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.group.slug,)),
            reverse('posts:profile', args=(self.user.username,))
        ]
        self.check_paginator(urls)

    def test_paginator_without_group_urls(self):
        """Пагинатор списков без группы."""
        posts = [
            Post(
                text=f'test post {i}',
                author=self.user,
            ) for i in range(POSTS_PER_PAGE + self.SECOND_PAGE_COUNT)
        ]
        Post.objects.bulk_create(posts)

        urls = [
            reverse('posts:posts_without_group'),
        ]
        self.check_paginator(urls)

    def check_paginator(self, urls):
        pages = [
            (1, POSTS_PER_PAGE),
            (2, self.SECOND_PAGE_COUNT),
        ]

        for url in urls:
            for page, count in pages:
                with self.subTest(url=url):
                    response = self.client.get(url, {'page': page})
                    self.assertEqual(
                        len(response.context.get('page_obj')),
                        count
                    )
