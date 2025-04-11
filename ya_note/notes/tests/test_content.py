from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.not_author = User.objects.create(username='tesNotAuthor')
        cls.author = User.objects.create(username='testAuthor')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        user_note_in_list = (
            (self.author, True),
            (self.not_author, False),
        )
        for user, note_in_list in user_note_in_list:
            self.client.force_login(user)
            with self.subTest(user=user):
                response = self.client.get(reverse('notes:list'))
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, note_in_list)

    def test_pages_contain_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
