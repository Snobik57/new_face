import pytest
from numpy import ndarray

from ..recognition.recognition_func import percent, new_load_image_file, get_image_vector, compare_faces_

testdata_percent = [
    (8, 80, 10.00),
    (8.0, 80.0, 10.00),
    (25, 180, 13.89)
]


@pytest.mark.parametrize('a, b, result', testdata_percent)
def test_percent(a, b, result):
    func_result = percent(a, b)
    assert func_result == result


testdata_percent = [
    ('f', 80, TypeError),
    ([8.0], {80.0}, TypeError),
    (True, None, TypeError)
]


@pytest.mark.xfail
@pytest.mark.parametrize('a, b, result', testdata_percent)
def test_fail_percent(a, b, result):
    func_result = percent(a, b)
    assert func_result == result


testdata_new_load_image_file = [
    ('face_compare/tests/photo_test/photo_410282.jpeg', 700, 'RGB'),
    ('face_compare/tests/photo_test/photo_410282.jpeg', 900, 'L'),
    ('face_compare/tests/photo_test/photo_410282.jpeg', 500, "RGB")
]


@pytest.mark.parametrize('a, b, c', testdata_new_load_image_file)
def test_parametrize_new_load_image_file(a, b, c):
    assert isinstance(new_load_image_file(a, b, c), ndarray)


def test_get_image_vector():
    result = get_image_vector('face_compare/tests/photo_test/photo_410282.jpeg')
    assert isinstance(result, list)
    assert isinstance(result[0], ndarray)
