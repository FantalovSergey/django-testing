from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    NAMESPACE = 'notes:'

    @classmethod
    def setUpTestData(cls):
        cls.not_author = User.objects.create(username='testNotAuthor')
        cls.author = User.objects.create(username='testAuthor')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )

    def test_pages_availability_for_anonymous_user(self):
        names = ('notes:home', 'users:login', 'users:logout', 'users:signup')
        for name in names:
            with self.subTest(name=name):
                if 'logout' in name:
                    response = self.client.post(reverse(name))
                else:
                    response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        for name in ('list', 'success', 'add'):
            with self.subTest(name=name):
                url = reverse(self.NAMESPACE + name)
                self.client.force_login(self.not_author)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.not_author, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('edit', 'detail', 'delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(
                        self.NAMESPACE + name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            ('list', None),
            ('success', None),
            ('add', None),
            ('edit', (self.note.slug,)),
            ('detail', (self.note.slug,)),
            ('delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(self.NAMESPACE + name, args=args)
                redirect_url = f'{reverse('users:login')}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
