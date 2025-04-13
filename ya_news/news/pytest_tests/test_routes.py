from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf

URL_HOME = lf('url_home')
URL_DETAIL = lf('url_detail')
URL_LOGIN = lf('url_login')
URL_LOGOUT = lf('url_logout')
URL_SIGNUP = lf('url_signup')
AUTHOR_CLIENT = lf('author_client')
READER_CLIENT = lf('reader_client')
URL_EDIT_COMMENT = lf('url_edit_comment')
URL_DELETE_COMMENT = lf('url_delete_comment')


@pytest.mark.parametrize(
    'url', (URL_HOME, URL_DETAIL, URL_LOGIN, URL_LOGOUT, URL_SIGNUP))
def test_pages_availability(client, url):
    if 'logout' in url:
        response = client.post(url)
    else:
        response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (AUTHOR_CLIENT, HTTPStatus.OK),
        (READER_CLIENT, HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize('url', (URL_EDIT_COMMENT, URL_DELETE_COMMENT))
def test_availability_for_comment_edit_and_delete(
        parametrized_client, expected_status, url):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('url', (URL_EDIT_COMMENT, URL_DELETE_COMMENT))
def test_redirect_for_anonymous_client(client, url, url_login):
    assertRedirects(client.get(url), f'{url_login}?next={url}')
