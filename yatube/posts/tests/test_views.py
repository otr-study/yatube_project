# posts/tests/views_urls.py
from core.test_utils import Post, PostTestCase
from django.core.paginator import Page
from django.test import Client
from django.urls import reverse


class PostViewTests(PostTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.POSTS_PER_PAGE = 10
        cls.POSTS_ANOTHER_GRUOP = 3
        cls.POSTS_ANOTHER_USER = 3
        for i in range(cls.POSTS_PER_PAGE):
            cls.create_post(postfix=str(i))

        cls.another_group = cls.create_group(
            title='Другая тестовая группа',
            slug='another_tst_slug'
        )
        for i in range(cls.POSTS_ANOTHER_GRUOP):
            cls.create_post(
                postfix=str(i + cls.POSTS_PER_PAGE),
                group=cls.another_group
            )

        cls.another_user = cls.create_user(username='another_user')
        for i in range(cls.POSTS_ANOTHER_USER):
            cls.create_post(
                postfix=str(i + cls.POSTS_PER_PAGE + cls.POSTS_ANOTHER_GRUOP),
                user=cls.another_user
            )
        cls.total_posts_count = Post.objects.count()

    def setUp(self):
        self.client = Client()
        self.client.force_login(PostViewTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:posts_without_group'): 'posts/group_list.html',
            reverse(
                'posts:group_list',
                args=(PostViewTests.group.slug,)
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                args=(PostViewTests.user.username,)
            ): 'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                args=(PostViewTests.post.id,)
            ): 'posts/create_post.html',
            reverse(
                'posts:post_detail',
                args=(PostViewTests.post.id,)
            ): 'posts/post_detail.html',
        }
        for reverse_name, template in pages_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context_paginator(self):
        response = self.client.get(reverse('posts:index'))
        page_obj = response.context.get('page_obj')
        self.assertIsInstance(page_obj, Page)
        self.assertEqual(len(page_obj), PostViewTests.POSTS_PER_PAGE)
        self.assertIsInstance(page_obj[0], Post)

        response = self.client.get(reverse('posts:index'))


