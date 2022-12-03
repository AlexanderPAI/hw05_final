from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group


User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='test_user')

        cls.group = Group.objects.create(
            title='Test_group',
            slug='Test_slug',
            description='Test_description'
        )

    def setUp(self):
        self.guest_client = Client()

    def test_index_cache(self):
        """
        Не понятно зачем тестировать кэш, но вот тест.
        """
        post = Post.objects.create(
            text='test',
            author=self.user,
            group=self.group
        )
        url = reverse('posts:index')
        response = self.guest_client.get(url)
        cached_response_content = response.content

        post.delete()

        response = self.guest_client.get(url)
        self.assertEqual(cached_response_content, response.content)

        cache.clear()

        response = self.guest_client.get(url)
        self.assertNotEqual(cached_response_content, response.content)
