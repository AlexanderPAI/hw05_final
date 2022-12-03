import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from http import HTTPStatus

from ..models import Post, Group, Follow

# Чтобы при изменении количества постов для паджинатора сюда это
# количество передавалось автоматом для теста паджинатора
from ..views import POSTS


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Тестовый пользователь
        cls.user = User.objects.create(username='test_user')

        # Тестовая группа Основная
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='description_of_test_group'
        )

        # Дополнительная тестовая группа для проверки: не попал ли пост
        # в группу, для которой не предназначен
        cls.wrong_group = Group.objects.create(
            title='wrong_group',
            slug='wrong_slug',
            description='wrong_group_description'
        )

        # Тестовый пост
        cls.post = Post.objects.create(
            text='Test_post',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        # Авторизованный тестовый пользователь
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Posts: namespaces используют соответствующие шаблоны."""
        tempales_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{self.group.slug}'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.post.id}'}
            ): 'posts/create_post.html'
        }

        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for reverse_name, template in tempales_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_list_show_correct_context(self):
        """
        Posts: В шаблоны со списком постов передается
        корректный контекст.
        """
        # В методе проверяется контекст шаблонов index, group_list, profile
        page_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}),
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            )
        ]

        # Проверка ключей author, text, pub_date во всех трех шаблонах
        for page in page_list:
            response = self.authorized_client.get(page)
            first_post = response.context['page_obj'][0]
            context_dict = {
                first_post.author: self.post.author,
                first_post.text: self.post.text,
                first_post.pub_date: self.post.pub_date
            }
            for field, expected in context_dict.items():
                with self.subTest(field=field):
                    self.assertEqual(field, expected)

        # Проверка ключей group.title и group.description в шаблоне group_list
        response_group_list = self.authorized_client.get(page_list[1])
        group = response_group_list.context['group']
        context_dict_group_list = {
            group.title: self.group.title,
            group.description: self.group.description
        }
        for field, expected in context_dict_group_list.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

        # Проверка ключей author, count в шаблоне profile
        response_profile = self.authorized_client.get(page_list[2])
        context_dict_profile = {
            response_profile.context['author']: self.user,
            response_profile.context['count']: self.user.posts.count()
        }

        for field, expected in context_dict_profile.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_create_edit_show_correct_context(self):
        """
        Posts: Шаблоны create, post_edit сформированы с правильным контекстом.
        """
        page_list = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'})
        ]

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for page in page_list:
            response = self.authorized_client.get(page)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    # Проверяет, что поле формы является экземпляром
                    # указанного класса
                    self.assertIsInstance(form_field, expected)

    def test_post_detail_show_correct_context(self):
        """Posts: Шаблон post_detail сформирован с правильным контестом"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}
        ))

        #  Констекст страницы
        post_context = response.context['post']
        post_author = post_context.author
        post_text = post_context.text
        post_pub_date = post_context.pub_date
        count_context = response.context['count']

        # Проверка контекста
        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_pub_date, self.post.pub_date)
        self.assertEqual(count_context, self.user.posts.count())

    def test_post_has_group_show_correct(self):
        """
        Posts: Если у поста есть группа, этот пост появляется
        на index, group_list, profile
        """
        post = self.post
        group = post.group
        page_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}),
            reverse('posts:profile', kwargs={
                'username': f'{self.user.username}'
            })
        ]

        if group is not None:
            for page in page_list:
                with self.subTest(page=page):
                    response = self.authorized_client.get(page)
                    post_on_page = response.context['page_obj'][0]
                    self.assertEqual(post_on_page, post)

    def test_wrong_group(self):
        """Posts: Посту верно присваивается группа"""
        post = self.post
        self.assertEqual(post.group, self.group)
        self.assertNotEqual(post.group, self.wrong_group)


class PaginatorViewsTest(TestCase):
    # Проверку паджинатора вывел в отдельный класс, иначе в setUpClass
    # будет бардак
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user_paginator')

        cls.group = Group.objects.create(
            title='test_group_pag',
            slug='test_slug_pag',
            description='description_of_test_group_pag'
        )

        # через bulk_create, чтобы при создании
        # постов был 1 запрос в БД, а не 12
        cls.posts_list = list()

        for i in range(12):
            cls.posts_list.append(
                Post(
                    text='Test_post', author=cls.user, group=cls.group
                )
            )

        Post.objects.bulk_create(cls.posts_list)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator(self):
        """
        Posts: Paginator разделяет посты по 10 на страницу \n
        и содержание страницы соответствует ожидаемому.
        """
        names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}),
            reverse('posts:profile', kwargs={
                'username': f'{self.user.username}'
            })
        ]
        for name in names:
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertEqual(len(response.context['page_obj']), POSTS)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesWithImage(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='test_user')

        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='description_of_test_group'
        )

        image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='image.gif',
            content=image,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Test_post',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение,
        # изменение папок и файлов.
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_with_images(self):
        """
        Posts: Посты с изображениями передаются в контекст корректно.
        """
        # Проверка index, group_list, profile
        page_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}),
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            )
        ]

        # Проверка ключей только изображений на указанных страницах
        for page in page_list:
            response = self.authorized_client.get(page)
            first_post = response.context['page_obj'][0]
            self.assertEqual(
                first_post.image,
                self.post.image
            )

        # Проверка post_detail
        page = reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{self.post.id}'}
        )
        response = self.authorized_client.get(page)
        self.assertEqual(response.context['post'].image, self.post.image)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create(username='follower')
        cls.not_follower = User.objects.create(username='not_follower')
        cls.author = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='Test_group',
            slug='test_group',
            description='Test_description'
        )
        cls.urls = {
            'follow': reverse(
                'posts:profile_follow',
                kwargs={'username': f'{cls.author.username}'}
            ),
            'unfollow': reverse(
                'posts:profile_unfollow',
                kwargs={'username': f'{cls.author.username}'}
            ),
            'follow_index': reverse('posts:follow_index'),
        }

    def setUp(self):
        self.guest_client = Client()
        self.follower_client = Client()
        self.not_follower_client = Client()
        self.follower_client.force_login(self.follower)
        self.not_follower_client.force_login(self.not_follower)

    def test_auth_following_unfollowing(self):
        """
        Posts: Auth может подписываться/отписываться от Авторов.
        """
        # Подписка
        response_to_follow = self.follower_client.get(self.urls['follow'])
        self.assertEqual(response_to_follow.status_code, HTTPStatus.FOUND)

        # Проверка, что модель Follow создалась
        follow = Follow.objects.filter(
            user=self.follower,
            author=self.author
        ).exists()

        self.assertTrue(follow)

        # Отписка
        response_to_unfollow = self.follower_client.get(self.urls['unfollow'])
        self.assertEqual(response_to_unfollow.status_code, HTTPStatus.FOUND)

        # Проверка, что модель Follow удалилась
        follow = Follow.objects.filter(
            user=self.follower,
            author=self.author
        ).exists()

        self.assertFalse(follow)

    def test_following_context(self):
        """
        Новая запись пользователя появляется в ленте
        подписчиков и не появляется в ленте не подписанных.
        """

        self.follower_client.get(self.urls['follow'])

        post = Post.objects.create(
            text='Test_post',
            author=self.author,
            group=self.group,
        )

        response_follower = self.follower_client.get(self.urls['follow_index'])
        response_not_follower = self.not_follower_client.get(
            self.urls['follow_index']
        )

        context_follower = response_follower.context['page_obj']
        context_not_follower = response_not_follower.context['page_obj']
        self.assertIn(post, context_follower)
        self.assertNotIn(post, context_not_follower)
