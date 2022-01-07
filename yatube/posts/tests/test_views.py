from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Follow, Group, Post, User
from .test_utils import PostTestCase, clear_cache

POSTS_PER_PAGE = getattr(settings, 'POSTS_PER_PAGE', 10)


class PostViewTests(PostTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.another_group = cls.create_group(
            title='Другая тестовая группа',
            slug='another_tst_slug'
        )
        cls.another_user = cls.create_user(username='another_user')
        image = cls.create_img(filename='tst_view_context.gif')
        cls.post_another_user = cls.create_post(
            user=cls.another_user,
            image=image
        )
        cls.post_another_group = cls.create_post(
            group=cls.another_group,
            image=image
        )
        cls.post_without_group = cls.create_post(
            empty_group=True,
            image=image
        )

    def setUp(self):
        self.client.force_login(self.user)

    @clear_cache
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

    @clear_cache
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
        comment = self.create_comment()
        response = self.client.get(
            reverse('posts:post_detail', args=(self.post.id,))
        )
        received_post = response.context.get('post')
        self.check_post_context(received_post, self.post)
        self.assertIsInstance(response.context.get('form'), CommentForm)
        self.assertIn(comment, received_post.comments.all())

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

    @clear_cache
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
                    'Пост без группы выводится на страницу профайл.'
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
            response = self.client.get(url)
            for func, description in checks:
                with self.subTest(url=url, description=description):
                    self.assertTrue(func(response.context.get('page_obj')))

    def check_post_context(self, post, post_standard):
        self.assertIsInstance(post, Post)
        self.assertEqual(post.text, post_standard.text)
        self.assertEqual(post.group, post_standard.group)
        self.assertEqual(post.author, post_standard.author)
        self.assertEqual(post.image, post_standard.image)


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
        cls.SECOND_PAGE_COUNT = max(1, POSTS_PER_PAGE // 2)

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


class CacheViewTests(PostTestCase):
    def test_cache_main_page(self):
        """Страница index возвращается из кеша."""
        url = reverse('posts:index')
        post_text = self.post.text.strip()
        self.client.get(url)
        self.post.delete()
        response = self.client.get(url)
        self.assertContains(response, post_text)
        cache.clear()
        response = self.client.get(url)
        self.assertNotContains(response, post_text)


class FollowViewTests(PostTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = cls.create_user(username='follower')
        cls.another_author = cls.create_user(username='another_author')
        cls.another_post = cls.create_post(
            user=cls.another_author,
            text='Пост автора без подписки',
        )

    def setUp(self):
        self.client.force_login(self.follower)

    def test_urls_followings_available_anonymus(self):
        """Доступность страницы подписок анонимусу."""
        client = Client()
        response = client.get(reverse('posts:follow_index'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_appears_feed_follower(self):
        """Пост корректно попадает в ленту подписчика."""
        self.create_follow(user=self.follower)
        response = self.client.get(reverse('posts:follow_index'))
        page_obj = response.context.get('page_obj')
        self.assertIn(self.post, page_obj)
        self.assertNotIn(self.another_post, page_obj)

    def test_create_delete_follower(self):
        """Проверка добавления/удаления подписок"""
        self.client.get(
            reverse(
                'posts:profile_follow',
                args=(self.another_author.username,)
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                author=self.another_author,
                user=self.follower,
            ).exists()
        )
        self.client.get(
            reverse(
                'posts:profile_unfollow',
                args=(self.another_author.username,)
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                author=self.another_author,
                user=self.follower,
            ).exists()
        )
