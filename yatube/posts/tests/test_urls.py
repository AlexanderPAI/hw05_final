from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Тестовый пользователь
        cls.user = User.objects.create(username='auth')
        cls.author = User.objects.create(username='author')
        # Тестовая группа
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Описание тестовой группы'
        )
        # Тестовый пост
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )

    def setUp(self):

        # Неавторизированный пользователь
        self.guest_client = Client()

        # Авторизованный пользователь
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.authorized_user_author = Client()
        self.authorized_user_author.force_login(self.author)

    def test_templates(self):
        """Posts: URL-адреса используют правильные шаблоны"""
        templates_url_name = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.author.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

        for address, template in templates_url_name.items():
            with self.subTest(address=address):
                response = self.authorized_user_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_pages_for_everyone(self):
        """Posts: Проверка доступа общих страниц"""
        url_list = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.id}/'
        )

        for url in url_list:
            with self.subTest(url=url):
                responce = self.guest_client.get(url)
                self.assertEqual(responce.status_code, HTTPStatus.OK)

    def test_pages_for_auth_by_anonymus(self):
        """
        Posts: Проверка доступа для Anonymous к страницам создания
        и редактирования и проверка редиректа для Anonymous.
        """
        url_list = (
            '/create/',
            f'/posts/{self.post.id}/edit/'
        )

        for url in url_list:
            with self.subTest(url=url):
                responce = self.guest_client.get(url, follow=True)
                self.assertRedirects(responce, f'/auth/login/?next={url}')

    def test_create_by_auth(self):
        """Posts: Проверка доступа Auth к странице создания"""
        responce = self.authorized_user.get('/create/')
        self.assertEqual(responce.status_code, HTTPStatus.OK)

    def test_edit_by_author(self):
        """Posts: Проверка доступа Author к странице редактирования"""
        responce = self.authorized_user_author.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(responce.status_code, HTTPStatus.OK)

    def test_redirect_edit_auth(self):
        """Posts: Проверка редиректа Anonymous со страницы редактирования"""
        responce = self.authorized_user.get(
            f'/posts/{self.post.id}/edit/',
            follow=True
        )
        self.assertRedirects(responce, f'/posts/{self.post.id}/')

    def test_404(self):
        """Posts: Проверка несуществующей страницы"""
        responce = self.authorized_user.get('/this_page_not_exists/')
        self.assertEqual(responce.status_code, HTTPStatus.NOT_FOUND)
