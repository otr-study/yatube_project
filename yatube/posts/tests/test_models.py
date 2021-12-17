# posts/tests/test_models.py
from core.test_utils import PostTestCase


class PostsModelsTest(PostTestCase):
    def test_post_models_have_correct_object_names(self):
        post = PostsModelsTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_post_verbose_name(self):
        post = PostsModelsTest.post
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

    def test_post_help_text(self):
        post = PostsModelsTest.post
        field_help_texts = {
            'text': 'Введите текст записи',
            'group': 'Выберите группу',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_group_models_have_correct_object_names(self):
        group = PostsModelsTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_group_verbose_name(self):
        group = PostsModelsTest.group
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Идентификатор',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_group_help_text(self):
        group = PostsModelsTest.group
        expected = (
            'Может содержать символы английского алфавита '
            'цифры и символы: "_", "-".'
        )
        self.assertEqual(group._meta.get_field('slug').help_text, expected)
