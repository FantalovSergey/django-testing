from django.contrib.auth import get_user_model

from .conftest import BaseTest
from notes.forms import NoteForm

User = get_user_model()


class TestContent(BaseTest):

    def test_notes_list_for_different_users(self):
        client_note_in_list = (
            (self.author_client, True),
            (self.not_author_client, False),
        )
        for client, note_in_list in client_note_in_list:
            with self.subTest(client=client):
                response = client.get(self.url_notes)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, note_in_list)

    def test_pages_contain_form(self):
        urls = (self.url_add, self.url_edit)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
