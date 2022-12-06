import time
from datetime import datetime
from typing import List
import PIL.Image
import face_recognition as fr
import numpy as np
from numpy import ndarray

from models.ch_db import DataBaseChORM


DATABASE = DataBaseChORM()


def percent(num: int or float, total: int or float) -> float:
    """
    Подсчитывает процент от num к total.

    :param num: число, процент которого нужно выяснить.
    :param total: общее число (100%).

    :return: процент от числа.
    """
    if isinstance(num, (int, float)) and isinstance(total, (int, float)):
        result = (num * 100) / total
        return float("{:.2f}".format(result))
    else:
        raise TypeError


def new_load_image_file(file: str, width: int = 1080, mode='RGB') -> ndarray:
    """
    Преобразует изображение (.jpg, .png, etc) в numpy array

    :param width: величина ширины для получения измененного размера изображения
    :param file: название или путь изображения
    :param mode: формат, в который нужно преобразовать изображение.
                 По-умолчанию 'RGB' (8-bit RGB, 3 channels), и 'L' (черно-белый) поддерживается.

    :return: изображение в виде numpy array
    """
    im = PIL.Image.open(file)

    if mode and mode == 'L' or mode == 'RGB':
        im = im.convert(mode)

    if im.size[0] > width:
        ratio = width / im.size[0]
        height = int((float(im.size[1]) * float(ratio)))
        im = im.resize((width, height), PIL.Image.Resampling.LANCZOS)

    return np.array(im)


def get_image_embedding(image_path: str, width: int = 1080) -> List[ndarray]:
    """
    Считывает на изображении лица и преобразует их в 128-мерный массив векторов.
    Сохраняет массивы в список и возвращает.

    :param width: величина ширины для получения измененного размера изображения.
    :param image_path: название или путь изображения.

    :return: список из массивов.
    """

    if image_path.split('.')[-1] in ['jpeg', 'jpg', 'png']:

        img = new_load_image_file(image_path, width=width)
        face_locations = fr.face_locations(img, model='cnn')
        img_encoding = fr.face_encodings(img, face_locations, model='large', num_jitters=2)

    else:
        raise TypeError('Image format not suitable')

    return img_encoding


def compare_faces_(attachments_embeddings: List[dict], image_embedding: List[ndarray], analytics_image: tuple) -> dict:
    """
    Сравнивает эмбеддинг аналитического изображения со списком кандидатов(эмбеддингов) из БД.

    :param analytics_image: данные об аналитическом изображении из БД
    :param attachments_embeddings: список эмбеддингов из БД (векторное представление изображения).
    :param image_embedding: эмбеддинг аналитического изображение (векторное представление изображения).

    :return: Словарь result_dict = {
            'match_found': match,
            'match_not_found': not_match,
        }
    """

    if isinstance(attachments_embeddings, list) and isinstance(image_embedding, list):

        created_at = datetime.now()

        for attachment in attachments_embeddings:

            start_time = time.time()

            result = fr.compare_faces([image_embedding], attachment['faces'], tolerance=0.485)
            match_found = 1 if True in result else 0

            DATABASE.insert_in_compare_faces(
                image_id=analytics_image[0],
                attachment_id=attachment['link_id'],
                match_found=match_found,
                match_execution_time=time.time()-start_time,
                created_at=created_at,
            )

        all_compare = DATABASE.select_result_faces_compare_faces(image_id=analytics_image[0])
        match = [i for i in all_compare if i[2] == 1]
        not_match = [i for i in all_compare if i[2] == 0]

        result_dict = {
            'match_found': match,
            'match_not_found': not_match,
        }
        return result_dict

    else:
        raise TypeError('attachments_embeddings, image_embedding: can only be a list')
