from django.test import TestCase

from .test_utils import Group, PostTestCase


class PostModelTest(PostTestCase):
    def test_models_have_correct_object_names(self):
        post = self.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_verbose_name(self):
        post = self.post
        field_verboses = {
            'text': 'Содержимое поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = self.post
        field_help_texts = {
            'text': 'Введите текст записи',
            'group': 'Выберите группу',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Описание тестовой группы',
        )

    def test_models_have_correct_object_names(self):
        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, str(self.group))

    def test_verbose_name(self):
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Идентификатор',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        expected = (
            'Может содержать символы английского алфавита '
            'цифры и символы: "_", "-".'
        )
        self.assertEqual(
            self.group._meta.get_field('slug').help_text,
            expected
        )
