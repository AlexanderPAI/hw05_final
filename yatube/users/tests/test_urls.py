from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus


User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')

    def setUp(self):
        # Неавторизованный пользователь
        self.guest_client = Client()
        # Авторизованный пользователь
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_URLs_responds_OK_unauth(self):
        """Users: URL-адреса unauth доступны"""
        url_list = [
            '/auth/signup/',
            '/auth/login/',
            '/auth/logout/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/<uidb64>/<token>/',
            '/auth/reset/done/'
        ]

        for url in url_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_URLs_reponds_OK_auth(self):
        """Users: URL-адреса auth доступны"""
        url_list = [
            '/auth/password_change/',
            '/auth/password_change/done/'
        ]

        for url in url_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_URLs_templates_unauth(self):
        """
        Users: URL-адреса неавтор.клиента используют соответствующие шаблоны.s
        """
        template_url_addresses = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/':
            'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }

        for reverse_name, template in template_url_addresses.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_URLs_templates_auth(self):
        """
        Users: URL-адреса автор.клиента используют соответствующие шаблоны.
        """
        template_url_addresses = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html'
        }

        for reverse_name, template in template_url_addresses.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
