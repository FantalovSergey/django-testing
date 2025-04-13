import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.usefixtures('many_news')
def test_news_count(client, url_home):
    response = client.get(url_home)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('many_news')
def test_news_order(client, url_home):
    response = client.get(url_home)
    dates = [news.date for news in response.context['object_list']]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.usefixtures('many_comments')
def test_comments_order(client, url_detail):
    response = client.get(url_detail)
    assert 'news' in response.context
    comments = response.context['news'].comment_set.all()
    timestamps = [comment.created for comment in comments]
    assert timestamps == sorted(timestamps)


def test_anonymous_client_has_no_form(client, url_detail):
    response = client.get(url_detail)
    assert 'form' not in response.context


def test_authorized_client_has_form(reader_client, url_detail):
    response = reader_client.get(url_detail)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
