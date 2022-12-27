import datetime
from typing import List

import pytest
from clickhouse_driver import Client
from ..models import DataBaseChORM
import os
from dotenv import load_dotenv

load_dotenv()

client_test = Client(
            user=os.getenv('user'),
            password=os.getenv('password'),
            host=os.getenv('host'),
            port=os.getenv('port'),
            database=os.getenv('test_database'),
        )

class TestDataBaseChORM(DataBaseChORM):
    pass

@pytest.fixture()
def setup():
    os.system(
        f"""clickhouse-client --password {os.getenv('password')} --query "CREATE DATABASE IF NOT EXISTS {os.getenv('test_database')}" """
    )
    TestDataBaseChORM(client=client_test).create_table()
    TestDataBaseChORM(client=client_test).client_recognition.execute(
        "INSERT INTO analytics_images VALUES",
        [{'id': 1,
          'person_name': 'test_string',
          'image_path': 'test/string',
          'created_at': datetime.datetime.now()}]
    )
    TestDataBaseChORM(client=client_test).client_recognition.execute(
        "INSERT INTO attachments VALUES",
        [{'id': 1,
          'link': 'link/test_string',
          'created_at': datetime.datetime.now()}]
    )
    yield
    pass


@pytest.fixture()
def teardown():
    pass
    yield
    os.system(
        f"""clickhouse-client --password {os.getenv('password')} --query "DROP DATABASE IF EXISTS {os.getenv('database')}" """
    )


def test_create_table(setup):
    result = TestDataBaseChORM(client=client_test).create_table()
    expectancy = [
        ('analytics_image_embedding',),
        ('analytics_images',),
        ('attachments',),
        ('attachments_embedding',),
        ('compare_faces',),
        ('result',)
    ]

    assert result == expectancy


def test_insert():
    result_attachments_embedding = TestDataBaseChORM(client=client_test).insert_in_attachments_embedding(
        attachment_id=1,
        face_available=0,
        connect_available=0,
        embedding={1, 2, 3},
        timestamp=datetime.datetime.now()
    )
    result_compare_faces = TestDataBaseChORM(client=client_test).insert_in_compare_faces(
        image_id=1,
        attachment_id=1,
        match_found=1,
        match_execution_time=1.2,
        created_at=datetime.datetime.now(),
    )
    result_analytics_image_embedding = TestDataBaseChORM(client=client_test).insert_in_analytics_image_embedding(
        image_id=1,
        person_name='test_string',
        embedding={1, 2, 3}
    )
    result_result = TestDataBaseChORM(client=client_test).insert_in_result(
        image_id=1,
        inspected=1,
        person_name='test_string',
        attachments_ids=[1],
        matches_found=1,
        matches_found_percent=100.0,
        no_matches_found=0,
        no_matches_found_percent=0.0,
        match_execution_time=1.1,
        created_at=datetime.datetime.now(),
    )

    assert result_attachments_embedding == 1
    assert result_compare_faces == 1
    assert result_analytics_image_embedding == 1
    assert result_result == 1

def test_select_all_analytics_images():
    result = TestDataBaseChORM(client=client_test).select_all_analytics_images()
    expectancy = 'test_string'

    assert isinstance(result, List)
    assert result[0][1] == expectancy

def test_select_all_with_result():
    result = TestDataBaseChORM(client=client_test).select_all_with_result(1)
    expectancy = 100.0

    assert isinstance(result, tuple)
    assert result[4] == expectancy

def test_select_result_faces_compare_faces():
    result = TestDataBaseChORM(client=client_test).select_result_faces_compare_faces(1)
    expectancy = 1.2

    assert len(result) == 1
    assert isinstance(result, List)
    assert result[0][3] == expectancy
    assert len(result[0]) == 5

def test_select_attachments_match_found():
    result = TestDataBaseChORM(client=client_test).select_attachments_match_found(1)

    assert len(result) == 1
    assert isinstance(result, List)
    assert result[0][0] == 1
    assert len(result[0]) == 1

def test_select_all_analytics_images_embeddings():
    result = TestDataBaseChORM(client=client_test).select_all_analytics_images_embeddings()

    assert len(result) == 1
    assert isinstance(result, List)
    assert result[0][1] == 'test_string'
    assert len(result[0]) == 3

def test_select_all_attachments():
    result = TestDataBaseChORM(client=client_test).select_all_attachments()

    assert isinstance(result, List)
    assert len(result) == 0

def test_select_all_images_in_compare_face():
    result = TestDataBaseChORM(client=client_test).select_all_images_in_compare_face()

    assert len(result) == 1
    assert isinstance(result, List)
    assert result[0] == 1

def test_select_all_with_attachments_embedding():
    result = TestDataBaseChORM(client=client_test).select_all_with_attachments_embedding(1)

    assert isinstance(result, List)
    assert len(result) == 0

def test_select_id_with_attachments_embedding():
    result = TestDataBaseChORM(client=client_test).select_id_with_attachments_embedding()

    assert len(result) == 1
    assert isinstance(result, List)
    assert result[0] == 1

def test_database_inspection():
    result = TestDataBaseChORM(client=client_test).database_inspection()

    assert len(result) == 1
    assert isinstance(result, List)
    assert result[0][1] == 'test_string'
    assert len(result[0]) == 4

def test_drop_table(teardown):
    result = TestDataBaseChORM(client=client_test).drop_table('compare_faces')

    assert isinstance(result, List)