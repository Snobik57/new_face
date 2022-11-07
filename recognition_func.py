import asyncio
import time
import os
import face_recognition as fr
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(1)
loop = asyncio.get_event_loop()


async def get_image_vector(image_path: str):
    # Считываем лицо, которое будем сравнивать. Получаем массив чисел(Эмбендинг)
    if image_path.split('.')[1] in ['jpeg', 'jpg', 'png']:
        # start_time = time.time()

        img1 = await loop.run_in_executor(_executor, fr.load_image_file, image_path)
        face_locations = await loop.run_in_executor(_executor, fr.face_locations, img1)
        # Бутылочное горлышко
        img1_encoding = await loop.run_in_executor(_executor, fr.face_encodings, img1, face_locations)

        # print(time.time() - start_time)
    else:
        raise TypeError('Image format not suitable')

    return img1_encoding


async def compare_faces_(children_images: list, parent_image) -> list:
    """
        Функция парсит URl - link, получая изображение. Преобразует полученное изображение в эмбенддинг и
        сравнивает его с родительским эмбенддингом - parent_image. Результат сравнения записывает в словарь.

        :param children_images: Пути до изображений
        :param parent_image: векторное представление родительского изображения

        :return:   [{
                'id': counter,
                'URL': link,
                'result': result,
                'time': time
            }]
    """
    list_ = []
    counter = 0

    for name_path in children_images:

        # Сравниваем эмбенддинги родительской и полученной фотографии
        start_time_down = time.time()

        # Создаем эмбенддинг полученной фотографии
        image_2_enc = await get_image_vector(name_path)

        if len(parent_image) > 0 and len(image_2_enc) > 0:
            result = await loop.run_in_executor(_executor, fr.compare_faces, [parent_image[0]], image_2_enc[0])

            bool_result = 'True' if True in result else 'False'
            os.remove(name_path)
            counter += 1
        # Сравниваем, если лиц на фотографии больше, чем одно.
        elif len(parent_image) > 0 and len(image_2_enc) > 1:

            result_list = []
            for img2_enc in image_2_enc:
                result = await loop.run_in_executor(_executor, fr.compare_faces, [parent_image], img2_enc)
                result_list.append(result)

            bool_result = 'True' if [True] in result_list else 'False'
            os.remove(name_path)
            counter += 1
        # Если лица на фотографии не найдены.
        else:
            os.remove(name_path)
            bool_result = 'Not found'
            counter += 1

        list_.append({
            'id': counter,
            'result': bool_result,
            'time_to_compare': time.time() - start_time_down
        })

    return list_
