from http import HTTPStatus

from django.contrib.auth import get_user_model

from .conftest import BaseTest

User = get_user_model()


class TestRoutes(BaseTest):

    def test_pages_availability_for_anonymous_user(self):
        for url in (self.url_home, self.url_login,
                    self.url_logout, self.url_signup):
            with self.subTest(url=url):
                if 'logout' in url:
                    response = self.client.post(url)
                else:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        for url in (self.url_notes, self.url_success, self.url_add):
            with self.subTest(url=url):
                response = self.not_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        clients_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.not_author_client, HTTPStatus.NOT_FOUND),
        )
        for client, status in clients_statuses:
            for url in (self.url_edit, self.url_detail, self.url_delete):
                with self.subTest(client=client, url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (self.url_notes, self.url_success, self.url_add,
                self.url_edit, self.url_detail, self.url_delete)
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.url_login}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
