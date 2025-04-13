from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment

User = get_user_model()


def test_anonymous_user_cant_create_comment(client, url_detail, form_data):
    client.post(url_detail, form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client, author, news, form_data, url_detail, url_to_comments):
    response = author_client.post(url_detail, form_data)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, bad_words_data, url_detail):
    response = author_client.post(url_detail, bad_words_data)
    assertFormError(response.context['form'], field='text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
        author_client, url_delete_comment, url_to_comments):
    assertRedirects(author_client.delete(url_delete_comment), url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        reader_client, url_delete_comment):
    response = reader_client.delete(url_delete_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        author_client, comment, url_edit_comment, form_data, url_to_comments):
    response = author_client.post(url_edit_comment, form_data)
    assertRedirects(response, url_to_comments)
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == form_data['text']
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author
    assert comment_from_db.created == comment.created


def test_user_cant_edit_comment_of_another_user(
        reader_client, comment, url_edit_comment, form_data):
    response = reader_client.post(url_edit_comment, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author
    assert comment_from_db.created == comment.created
