from datetime import datetime
from typing import List, Dict

import pytest
import pg8000.native
from minumtium.infra.database import DataNotFoundException
from minumtium.modules.posts import Post

from minumtium_postgres import MinumtiumPostgresAdapter, MinumtiumPostgresAdapterConfig


def test_find_by_id(adapter_with_data):
    assert adapter_with_data.find_by_id(id='1') == {'id': '1',
                                                    'title': 'This is the first post',
                                                    'author': 'danodic',
                                                    'timestamp': '2022-02-22 12:22:22.222222',
                                                    'body': 'This is a sample post.'}


def test_find_by_id_not_found(adapter_with_data):
    with pytest.raises(DataNotFoundException) as e:
        adapter_with_data.find_by_id(id='0')
        assert e.type is DataNotFoundException
        assert e.value.args[0] == "No data found at posts for id: 0"


def test_find_by_criteria(adapter_with_data):
    criteria = {
        'id': '9',
        'title': 'This is the ninetieth post'
    }
    assert adapter_with_data.find_by_criteria(criteria) == [{'id': '9',
                                                             'title': 'This is the ninetieth post',
                                                             'author': 'danodic',
                                                             'timestamp': '2022-02-22 04:22:22.222222',
                                                             'body': 'This is a sample post.'}]


def test_find_by_criteria_not_found(adapter_with_data):
    criteria = {
        'id': '11',
        'title': 'This is the ninetieth post'
    }
    with pytest.raises(DataNotFoundException) as e:
        adapter_with_data.find_by_criteria(criteria)
        assert e.type is DataNotFoundException
        assert e.value.args[0] == f'No data found for the following criteria: {str(criteria)}'


def test_insert(adapter_with_data, database_connection: pg8000.Connection):
    data = {'title': 'This is the first post',
            'author': 'danodic',
            'timestamp': datetime(2022, 2, 22, 12, 22, 22, 222222),
            'body': 'This is a sample post.'}

    inserted_id = adapter_with_data.insert(data)

    assert inserted_id == '11'

    inserted_data = database_connection.run("SELECT * FROM posts WHERE id=:id", id=inserted_id)
    assert inserted_data[0] == [
        11,
        'This is the first post',
        'danodic',
        'This is a sample post.',
        datetime(2022, 2, 22, 12, 22, 22, 222222)]


def test_all(adapter_with_some_data):
    assert adapter_with_some_data.all() == [{'id': '1',
                                             'title': 'This is the first post',
                                             'author': 'danodic',
                                             'timestamp': '2022-02-22 12:22:22.222222',
                                             'body': 'This is a sample post.'},
                                            {'id': '2',
                                             'title': 'This is the second post',
                                             'author': 'beutrano',
                                             'timestamp': '2022-02-22 11:22:22.222222',
                                             'body': 'This is a sample post.'}]


def test_all_with_limit(adapter_with_data):
    assert adapter_with_data.all(limit=2) == [{'id': '1',
                                               'title': 'This is the first post',
                                               'author': 'danodic',
                                               'timestamp': '2022-02-22 12:22:22.222222',
                                               'body': 'This is a sample post.'},
                                              {'id': '2',
                                               'title': 'This is the second post',
                                               'author': 'beutrano',
                                               'timestamp': '2022-02-22 11:22:22.222222',
                                               'body': 'This is a sample post.'}]


def test_all_with_data(adapter_with_data):
    assert adapter_with_data.all(limit=2, skip=2) == [{'id': '3',
                                                       'title': 'This is the third post',
                                                       'author': 'danodic',
                                                       'timestamp': '2022-02-22 10:22:22.222222',
                                                       'body': 'This is a sample post.'},
                                                      {'id': '4',
                                                       'title': 'This is the fourth post',
                                                       'author': 'danodic',
                                                       'timestamp': '2022-02-22 09:22:22.222222',
                                                       'body': 'This is a sample post.'}]


def test_summary(adapter_with_data):
    assert adapter_with_data.summary(['id', 'title', 'timestamp'], limit=5) == [{'id': '1',
                                                                                 'title': 'This is the first post',
                                                                                 'timestamp': '2022-02-22 12:22:22.222222'},
                                                                                {'id': '2',
                                                                                 'title': 'This is the second post',
                                                                                 'timestamp': '2022-02-22 11:22:22.222222'},
                                                                                {'id': '3',
                                                                                 'title': 'This is the third post',
                                                                                 'timestamp': '2022-02-22 10:22:22.222222'},
                                                                                {'id': '4',
                                                                                 'title': 'This is the fourth post',
                                                                                 'timestamp': '2022-02-22 09:22:22.222222'},
                                                                                {'id': '5',
                                                                                 'title': 'This is the fifth post',
                                                                                 'timestamp': '2022-02-22 08:22:22.222222'}]


def test_posts_parsing_full(adapter_with_data):
    data = adapter_with_data.find_by_id(id='1')
    parsed = Post.parse_obj(data)
    assert parsed.id == '1'
    assert parsed.title == 'This is the first post'
    assert parsed.author == 'danodic'
    assert parsed.body == 'This is a sample post.'
    assert parsed.timestamp == datetime(2022, 2, 22, 12, 22, 22, 222222)


def test_posts_parsing_summary(adapter_with_data):
    data = adapter_with_data.summary(['id', 'title', 'author', 'timestamp'], limit=1)[0]
    parsed = Post.parse_obj(data)
    assert parsed.id == '1'
    assert parsed.title == 'This is the first post'
    assert parsed.author == 'danodic'
    assert parsed.timestamp == datetime(2022, 2, 22, 12, 22, 22, 222222)


@pytest.fixture(scope='function')
def database_connection(adapter_config: MinumtiumPostgresAdapterConfig) -> pg8000.Connection:
    return pg8000.native.Connection(
        adapter_config.username,
        password=adapter_config.password)


def setup_database(database_connection: pg8000.Connection, schema_setup:str):
    database_connection.run(schema_setup)


def insert_data(posts_data: List[Dict], database_connection: pg8000.Connection):
    insert_sql = """
        INSERT INTO posts (title, author, body, timestamp)
        VALUES (:title, :author, :body, :timestamp)
    """

    for data in posts_data:
        database_connection.run(insert_sql, **data)


@pytest.fixture(scope='function')
def adapter_with_data(database_connection: pg8000.Connection,
                      adapter: MinumtiumPostgresAdapter,
                      posts_data: List[Dict]) -> MinumtiumPostgresAdapter:
    insert_data(posts_data, database_connection)
    return adapter


@pytest.fixture(scope='function')
def adapter_with_some_data(database_connection: pg8000.Connection,
                           adapter: MinumtiumPostgresAdapter,
                           posts_data: List[Dict]) -> MinumtiumPostgresAdapter:
    insert_data(posts_data[:2], database_connection)
    return adapter


@pytest.fixture(scope='function')
def adapter(database_connection: pg8000.Connection,
            adapter_config: MinumtiumPostgresAdapterConfig) -> MinumtiumPostgresAdapter:
    setup_database(database_connection)
    adapter = MinumtiumPostgresAdapter(adapter_config, 'posts')
    yield adapter
    database_connection.close()


@pytest.fixture()
def posts_data():
    return [{'id': '1',
             'title': 'This is the first post',
             'author': 'danodic',
             'timestamp': datetime(2022, 2, 22, 12, 22, 22, 222222),
             'body': 'This is a sample post.'},
            {'id': '2',
             'title': 'This is the second post',
             'author': 'beutrano',
             'timestamp': datetime(2022, 2, 22, 11, 22, 22, 222222),
             'body': 'This is a sample post.'},
            {'id': '3',
             'title': 'This is the third post',
             'author': 'danodic',
             'timestamp': datetime(2022, 2, 22, 10, 22, 22, 222222),
             'body': 'This is a sample post.'},
            {'id': '4',
             'title': 'This is the fourth post',
             'author': 'danodic',
             'timestamp': datetime(2022, 2, 22, 9, 22, 22, 222222),
             'body': 'This is a sample post.'},
            {'id': '5',
             'title': 'This is the fifth post',
             'author': 'danodic',
             'timestamp': datetime(2022, 2, 22, 8, 22, 22, 222222),
             'body': 'This is a sample post.'},
            {'id': '6',
             'title': 'This is the sixth post',
             'author': 'danodic',
             'timestamp': datetime(2022, 2, 22, 7, 22, 22, 222222),
             'body': 'This is a sample post.'},
            {'id': '7',
             'title': 'This is the seventh post',
             'author': 'danodic',
             'timestamp': datetime(2022, 2, 22, 6, 22, 22, 222222),
             'body': 'This is a sample post.'},
            {'id': '8',
             'title': 'This is the eightieth post',
             'author': 'danodic',
             'timestamp': datetime(2022, 2, 22, 5, 22, 22, 222222),
             'body': 'This is a sample post.'},
            {'id': '9',
             'title': 'This is the ninetieth post',
             'author': 'danodic',
             'timestamp': datetime(2022, 2, 22, 4, 22, 22, 222222),
             'body': 'This is a sample post.'},
            {'id': '10',
             'title': 'This is the tenth post',
             'author': 'danodic',
             'timestamp': datetime(2022, 2, 22, 3, 22, 22, 222222),
             'body': 'This is a sample post.'}]
