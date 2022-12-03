from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class UsersViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_namespace_use_correct_template_unauth(self):
        """
        Users: namespace:name для Anonymous используют коррекстные шаблоны.
        """
        template_url_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse(
                'users:password_reset_form'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': 'uidb64', 'token': 'token'}
            ): 'users/password_reset_confirm.html'
        }

        for reverse_name, template in template_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                renponse = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(renponse, template)

    def test_namespace_use_correct_template_auth(self):
        """Users: namespace:name для Auth используют корреrтные шаблоны"""
        template_url_names = {
            reverse(
                'users:password_change_form'
            ): 'users/password_change_form.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html'
        }

        for reverse_name, template in template_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                renponse = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(renponse, template)

    def test_signup_show_correct_context(self):
        """Users: /signup/ показывает форму для создания пользователя."""
        page = reverse('users:signup')
        form = UserCreationForm
        response = self.guest_client.get(page)
        context_form = response.context.get('form')
        self.assertIsInstance(context_form, form)
