from http import HTTPStatus

from django.test import Client, TestCase


class Pages404and403Test(TestCase):
    def setUp(self):
        self.client = Client()

    def test_404_error_page(self):
        """
        Core: Проверка кастомной страницы page_not_found_404.
        """
        response = self.client.get('/page_not_exists')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
