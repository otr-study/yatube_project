# posts/tests/test_views.py
from core.test_utils import Post, PostTestCase
from django import forms
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
        cls.POSTS_WITHOUT_GRUOP = 11
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

        for i in range(cls.POSTS_WITHOUT_GRUOP):
            cls.create_post(
                postfix=str(i + cls.POSTS_PER_PAGE + cls.POSTS_ANOTHER_GRUOP),
                empty_group=True
            )

        cls.another_user = cls.create_user(username='another_user')
        for i in range(cls.POSTS_ANOTHER_USER):
            cls.create_post(
                postfix=str(i + cls.POSTS_PER_PAGE
                            + cls.POSTS_ANOTHER_GRUOP
                            + cls.POSTS_WITHOUT_GRUOP
                            ),
                user=cls.another_user
            )
        cls.total_posts_count = Post.objects.count()
        cls.count_posts_group = (cls.total_posts_count
                                 - cls.POSTS_ANOTHER_GRUOP
                                 - cls.POSTS_WITHOUT_GRUOP)
        cls.count_posts_user = cls.total_posts_count - cls.POSTS_ANOTHER_USER

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
        """Контекст главной страницы и пагинатор."""
        count = PostViewTests.total_posts_count
        self.check_list_url(
            reverse('posts:index'),
            count,
            lambda x: PostViewTests.post in x
        )

    def test_profile_context_paginator(self):
        """Контекст страницы профайла и пагинатор."""
        job_preset = {
            reverse(
                'posts:profile',
                args=(PostViewTests.user.username,)
            ): (
                PostViewTests.count_posts_user,
                lambda x: PostViewTests.post in x
            ),
            reverse(
                'posts:profile',
                args=(PostViewTests.another_user.username,)
            ): (
                PostViewTests.POSTS_ANOTHER_USER,
                lambda x: PostViewTests.post not in x
            )
        }
        for url, params in job_preset.items():
            self.check_list_url(url, *params)

    def test_group_list_context_paginator(self):
        """Контекст страницы группы и пагинатор."""
        job_preset = {
            reverse(
                'posts:group_list',
                args=(PostViewTests.group.slug,)
            ): (
                PostViewTests.count_posts_group,
                lambda x: PostViewTests.post in x
            ),
            reverse(
                'posts:group_list',
                args=(PostViewTests.another_group.slug,)
            ): (
                PostViewTests.POSTS_ANOTHER_GRUOP,
                lambda x: PostViewTests.post not in x
            ),
            reverse(
                'posts:posts_without_group'
            ): (
                PostViewTests.POSTS_WITHOUT_GRUOP,
                lambda x: PostViewTests.post not in x
            )
        }
        for url, params in job_preset.items():
            self.check_list_url(url, *params)

    def test_post_detail_context(self):
        """Контекст страницы post_detail"""
        response = self.client.get(
            reverse('posts:post_detail', args=(PostViewTests.post.id,))
        )
        self.check_post_context(response.context.get('post'))

    def test_create_post_context(self):
        """Контекст формы добавления поста"""
        response = self.client.get(reverse('posts:post_create'))
        self.check_post_form_context(response.context.get('form'))

    def test_edit_post_context(self):
        """Контекст формы едактирования поста"""
        response = self.client.get(
            reverse('posts:post_edit', args=(PostViewTests.post.id,))
        )
        self.check_post_form_context(response.context.get('form'))

    def check_post_form_context(self, form):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = form.fields.get(value)
                self.assertIsInstance(form_field, expected)

    def check_post_context(self, post):
        self.assertIsInstance(post, Post)
        self.assertIn('Текст большого-пребольшого тестового поста', post.text)

    def check_list_url(self, url, count, func):
        page = 1
        all_posts = []
        while count > 0:
            cur_page = '' if page == 1 else f'?page={page}'
            cur_len = min(count, PostViewTests.POSTS_PER_PAGE)
            response = self.client.get(url + cur_page)
            page_obj = response.context.get('page_obj')
            self.assertIsInstance(page_obj, Page)
            self.assertEqual(len(page_obj), cur_len)
            all_posts = all_posts + list(page_obj)
            count -= PostViewTests.POSTS_PER_PAGE
            page += 1
        self.assertTrue(func(all_posts))
        self.check_post_context(all_posts[0])
