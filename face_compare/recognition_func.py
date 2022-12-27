import time
import PIL
import face_recognition as fr
import numpy as np
import cv2

from numpy import ndarray
from datetime import datetime
from typing import List

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


def compare_images(attachments_embeddings: List[dict], image_embedding: List[ndarray], analytics_image: tuple) -> dict:
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


def recognition_vidio(video_file_path: str, attachment_id: int) -> None:
    """
    Считывает видео по кадрам. Проводит распознавание на каждом пятом кадре.
    Заносит данные по видео в БД.
    Если высота и ширина кадра превышает 854х480, то кадр преобразуется в установленный

    @param video_file_path: путь к видео
    @param attachment_id: id аттачмента
    @return: None
    """
    input_movie = cv2.VideoCapture(video_file_path)
    length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))
    counter = 0
    result = False

    while True:

        counter += 1
        ret, face = input_movie.read()
        width = int(input_movie.get(3))
        height = int(input_movie.get(4))

        if width * height > 410000:
            percent_frame = ((((width * height) - 410000) * 100) / (width * height)) / 100
            width = int(width * percent_frame)
            height = int(height * percent_frame)
            face = cv2.resize(face, (width, height))

        if not ret or counter > 1800:
            return result

        elif ret and counter % 5 == 0:

            video_face_locations = fr.face_locations(face, model='cnn')
            video_face_encodings = fr.face_encodings(face, video_face_locations)

            if video_face_encodings:
                for embedding in video_face_encodings:
                    DATABASE.insert_in_attachments_embedding(
                        attachment_id=attachment_id,
                        face_available=1,
                        connect_available=1,
                        embedding=embedding,
                        timestamp=datetime.now(),
                    )

            else:
                DATABASE.insert_in_attachments_embedding(
                    attachment_id=attachment_id,
                    face_available=0,
                    connect_available=1,
                    embedding=np.array([]),
                    timestamp=datetime.now(),
                )
