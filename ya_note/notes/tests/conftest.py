from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new_slug'
        }
        cls.not_author = User.objects.create(username='testNotAuthor')
        cls.author = User.objects.create(username='testAuthor')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )
        cls.url_home = reverse('notes:home')
        cls.url_notes = reverse('notes:list')
        cls.url_add = reverse('notes:add')
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_detail = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_success = reverse('notes:success')
        cls.url_login = reverse('users:login')
        cls.url_logout = reverse('users:logout')
        cls.url_signup = reverse('users:signup')
