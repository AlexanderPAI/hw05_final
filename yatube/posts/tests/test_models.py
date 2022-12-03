from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from django.test import TestCase


from ..models import Group, Post, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Posts: Проверяем, что у моделей корректно работает __str__"""
        post = PostModelTest.post
        group = PostModelTest.group
        return_str = (
            str(post),
            str(group),
        )
        correct_return = (
            post.text[:15],
            group.title
        )
        self.assertEqual(return_str, correct_return)

    def test_verbose_name(self):
        """Posts: verbose_name в полях моделей совпадает с ожидаемым"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата создания',
            'author': 'Автор поста',
            'group': 'group',
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_test(self):
        """Posts: help_text в полях моделей совпадает с ожидаемым"""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }

        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value
                )


class FollowModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.author = User.objects.create(username='author')

    def test_unique_follow_model(self):
        """
        Posts: проверка уникальности подписок
        """
        Follow.objects.create(
            user=self.user,
            author=self.author
        )

        with self.assertRaises(IntegrityError):
            Follow.objects.create(
                user=self.user,
                author=self.author
            )
