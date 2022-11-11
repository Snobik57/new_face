import pytest
import sqlalchemy as sq
import numpy as np

from sqlalchemy_utils import drop_database, database_exists
from face_compare.tests.DB_test import DataBaseORM, DSN, create_database, Base, DATA


@pytest.fixture()
def setup():
    if not database_exists(sq.create_engine(DSN).url):
        create_database(sq.create_engine(DSN).url)
        Base.metadata.create_all(sq.create_engine(DSN))
        DataBaseORM().loaddata(DATA)
    else:
        pass
    yield
    pass


@pytest.fixture()
def teardown():
    pass
    yield
    if database_exists(sq.create_engine(DSN).url):
        drop_database(sq.create_engine(DSN).url)


def test_add_new_link(setup):
    assert DataBaseORM().add_new_link(
        'https://i.mycdn.me/i?r=AzEQ4zZsk-R8_et5CbSTMwY537btZnMO0N7pBiM9ZBG5M9f3rKh57jNiMJCkSAlKRWM'
    ) == 4


def test_add_new_face():
    assert DataBaseORM().add_new_face(
        4, np.array([-0.12025938,  0.0724209,  0.07819445, -0.03757837, -0.12934569])
    ) is True


def test_get_face_from_link():
    assert isinstance(DataBaseORM().get_face_from_link(
        'https://i.mycdn.me/i?r=AzEQ4zZsk-R8_et5CbSTMwY537btZnMO0N7pBiM9ZBG5M9f3rKh57jNiMJCkSAlKRWM'
    ), dict)


def test_get_all_faces():
    assert len(DataBaseORM().get_all_faces()) == 2


def test_get_all_links():
    assert len(DataBaseORM().get_all_links()) == 1


def test_get_link_id():
    assert DataBaseORM().get_link_id(
        'https://i.mycdn.me/i?r=AzEQ4zZsk-R8_et5CbSTMwY537btZnMO0N7pBiM9ZBG5MxkiwBwb6zn5zJNytXjxc88'
    ) == 3


def test_count_link_in_db():
    assert DataBaseORM().count_link_in_db(
        'https://i.mycdn.me/i?r=AzEQ4zZsk-R8_et5CbSTMwY537btZnMO0N7pBiM9ZBG5MxkiwBwb6zn5zJNytXjxc88'
    ) is True


def test_add_connect(teardown):
    assert DataBaseORM().add_connect(
        'https://i.mycdn.me/i?r=AzEQ4zZsk-R8_et5CbSTMwY537btZnMO0N7pBiM9ZBG5MxkiwBwb6zn5zJNytXjxc88',
        face_available=True,
        connect_available=True
    ) is True