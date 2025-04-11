from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    FORM_DATA_WITHOUT_SLUG = {
        'title': 'Заголовок',
        'text': 'Текст',
    }
    FORM_DATA = {'slug': 'slug'}
    FORM_DATA.update(FORM_DATA_WITHOUT_SLUG)

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='testAuthor')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.url_add = reverse('notes:add')
        cls.url_success = reverse('notes:success')

    def test_user_can_create_note(self):
        response = self.author_client.post(self.url_add, self.FORM_DATA)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.FORM_DATA['title'])
        self.assertEqual(note.text, self.FORM_DATA['text'])
        self.assertEqual(note.slug, self.FORM_DATA['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        expected_url = f'{reverse('users:login')}?next={self.url_add}'
        response = self.client.post(self.url_add, self.FORM_DATA)
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=self.FORM_DATA['slug'],
            author=self.author,
        )
        response = self.author_client.post(self.url_add, self.FORM_DATA)
        self.assertFormError(
            response.context['form'], 'slug', errors=(note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        response = self.author_client.post(
            self.url_add, self.FORM_DATA_WITHOUT_SLUG)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(
            note.slug, slugify(self.FORM_DATA_WITHOUT_SLUG['title']))


class TestNoteEditDelete(TestCase):
    FORM_DATA = {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug'
    }

    @classmethod
    def setUpTestData(cls):
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
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_success = reverse('notes:success')

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.url_edit, self.FORM_DATA)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.FORM_DATA['title'])
        self.assertEqual(self.note.text, self.FORM_DATA['text'])
        self.assertEqual(self.note.slug, self.FORM_DATA['slug'])

    def test_other_user_cant_edit_note(self):
        response = self.not_author_client.post(self.url_edit, self.FORM_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.url_delete)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        response = self.not_author_client.post(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
