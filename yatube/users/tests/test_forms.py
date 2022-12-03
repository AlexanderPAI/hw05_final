from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class UserCreateTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        """Users: Новый пользователь создается корректно"""
        form_data = {
            'first_name': 'Ivan',
            'last_name': 'Petrov',
            'username': 'ipetrov',
            'email': 'ipetrov@email.com',
            'password1': 'QvFgDlLoooPPss',
            'password2': 'QvFgDlLoooPPss',
        }

        user_counts = User.objects.count()

        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:index'))

        self.assertEqual(User.objects.count(), user_counts + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='Ivan',
                last_name='Petrov',
                username='ipetrov',
                email='ipetrov@email.com'
            ).exists()
        )
