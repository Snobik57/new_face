import time
from typing import List

import PIL
import face_recognition as fr
import numpy as np
from numpy import ndarray

from models.db_func import DataBaseORM

DATABASE = DataBaseORM()


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
    :param mode: формат, в который нужно преобразовать изображение. По-умолчанию 'RGB' (8-bit RGB, 3 channels),
     и 'L' (черно-белый) поддерживается.
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


def get_image_vector(image_path: str, width: int = 1080) -> List[ndarray]:
    """
    Считывает на изображении лица и преобразует их в 128-мерный массив векторов.
    Сохраняет массивы в список и возвращает.
    :param width:
    :param image_path: название или путь изображения.
    :return: список из массивов.
    """

    if image_path.split('.')[-1] in ['jpeg', 'jpg', 'png']:
        # Преобразует фотографию в массив чисел
        img = new_load_image_file(image_path, width=width)
        # Поиск лица на фотографии с помощью сверточной нейронной сети(cnn)
        face_locations = fr.face_locations(img, model='cnn')
        # Считываем лицо, которое будем сравнивать. Получаем массив векторов(эмбеддинг)
        img_encoding = fr.face_encodings(img, face_locations, model='large', num_jitters=2)

    else:
        raise TypeError('Image format not suitable')

    return img_encoding


def compare_faces_(children_images: List[dict], parent_image: List[ndarray], image_id) -> List[dict]:
    """
    Сравнивает эмбеддинг аналитического изображения со списком кандидатов(эмбеддингов) из БД.
    :param image_id:
    :param children_images: список эмбеддингов из БД (векторное представление изображения).
    :param parent_image: эмбеддинг аналитического изображение (векторное представление изображения).
    :return:   Объект модели SingleCompareFace
    """

    if isinstance(children_images, list) and isinstance(parent_image, list):

        for face in children_images:

            start_time_down = time.time()

            if len(parent_image) > 0:
                # Функция сравнения
                result = fr.compare_faces([parent_image[0]], face['faces'], tolerance=0.485)
                bool_result = True if True in result else False

                DATABASE.add_new_compare(
                    image_id=image_id,
                    face_id=face['face_id'],
                    match_found=bool_result,
                    match_execution_time=round(time.time() - start_time_down, 5)
                )

        return DATABASE.get_compare_from_image(image_id)

    else:
        raise TypeError('')


if __name__ == "__main__":
    pass
