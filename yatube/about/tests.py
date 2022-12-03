from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """About: URL-адреса доступны"""
        urls_list = (
            '/about/author/',
            '/about/tech/'
        )

        for url in urls_list:
            with self.subTest(url=url):
                responce = self.guest_client.get(url)
                self.assertEqual(responce.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """About: URL-адреса используют правильные шаблоны"""
        templates_url_name = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }

        for address, template in templates_url_name.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)


class AboutViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_accessible_by_name(self):
        """About: URL, генерируемый при помощи namespace, доступен"""
        page_list = [
            reverse('about:author'),
            reverse('about:tech')
        ]

        for page in page_list:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_pages_uses_correct_templare(self):
        """About: При запросе к namespace применяются корректные шаблоны"""
        tempales_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }

        for reverse_name, template in tempales_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
