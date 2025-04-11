from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (lf('url_home'), lf('url_detail'), lf('url_login'),
     lf('url_logout'), lf('url_signup'))
)
def test_pages_availability(client, url):
    if 'logout' in url:
        response = client.post(url)
    else:
        response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('author_client'), HTTPStatus.OK),
        (lf('reader_client'), HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize(
    'url',
    (lf('url_edit_comment'), lf('url_delete_comment'))
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, expected_status, url):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (lf('url_edit_comment'), lf('url_delete_comment'))
)
def test_redirect_for_anonymous_client(client, url, url_login):
    assertRedirects(client.get(url), f'{url_login}?next={url}')
