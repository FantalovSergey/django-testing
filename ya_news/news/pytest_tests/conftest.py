import pytest

from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import Comment, News

TEST_COMMENTS_COUNT = 10


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def many_news():
    all_news = [
        News(
            title=f'Новость {index}',
            text='Текст',
            date=datetime.today() - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(news=news, author=author, text='Комментарий')


@pytest.fixture
def many_comments(author, news):
    now = timezone.now()
    for index in range(TEST_COMMENTS_COUNT):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    return {'text': 'Новый комментарий'}


@pytest.fixture
def bad_words_data():
    return {'text': f'Текст, {BAD_WORDS[0]}'}


@pytest.fixture
def url_home():
    return reverse('news:home')


@pytest.fixture
def url_detail(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_to_comments(url_detail):
    return url_detail + '#comments'


@pytest.fixture
def url_delete_comment(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def url_edit_comment(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def url_login():
    return reverse('users:login')


@pytest.fixture
def url_logout():
    return reverse('users:logout')


@pytest.fixture
def url_signup():
    return reverse('users:signup')
