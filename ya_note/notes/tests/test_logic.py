from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from .conftest import BaseTest
from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestLogic(BaseTest):

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(self.url_add, self.form_data)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        initial_notes_count = Note.objects.count()
        expected_url = f'{self.url_login}?next={self.url_add}'
        response = self.client.post(self.url_add, self.form_data)
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), initial_notes_count)

    def test_not_unique_slug(self):
        initial_notes_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.url_add, self.form_data)
        self.assertFormError(
            response.context['form'], 'slug', self.note.slug + WARNING)
        self.assertEqual(Note.objects.count(), initial_notes_count)

    def test_empty_slug(self):
        Note.objects.all().delete()
        del self.form_data['slug']
        response = self.author_client.post(self.url_add, self.form_data)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(self.form_data['title']))

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.url_edit, self.form_data)
        self.assertRedirects(response, self.url_success)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.form_data['title'])
        self.assertEqual(note_from_db.text, self.form_data['text'])
        self.assertEqual(note_from_db.slug, self.form_data['slug'])
        self.assertEqual(note_from_db.author, self.note.author)

    def test_other_user_cant_edit_note(self):
        response = self.not_author_client.post(self.url_edit, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.note.author)

    def test_author_can_delete_note(self):
        initial_notes_count = Note.objects.count()
        response = self.author_client.post(self.url_delete)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), initial_notes_count - 1)

    def test_other_user_cant_delete_note(self):
        initial_notes_count = Note.objects.count()
        response = self.not_author_client.post(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_notes_count)
