import time
from datetime import datetime

from models.ch_db import DataBaseChORM
from recognition_func import get_image_vector, compare_faces_, percent


DATABASE = DataBaseChORM()


def gathering_information(analytics_image: tuple):
    """
    Сравнивает эмбеддинг изображения с данными из БД.
    Записывает результат в БД в таблицу analytics_images

    :param analytics_image: id изображения из БД

    :return: Возвращает список данных по полученному изображению из analytics_images
    """

    end_time = time.time()
    print(analytics_image[1])
    base_image = get_image_vector(f"{analytics_image[1]}")

    inter_list = DATABASE.select_all_with_media_images()
    result_list = compare_faces_(inter_list, base_image, analytics_image)

    counter_true = 0
    counter_false = 0

    for element in result_list:
        if element[3] == 1:
            counter_true += 1
        elif element[3] == 0:
            counter_false += 1

    DATABASE.insert_in_analytics_images(
        analytics_name=analytics_image[0],
        inspected=1,
        image_embedding=base_image[0],
        image_path=analytics_image[1],
        matches_found=counter_true,
        matches_found_percent=percent(counter_true, len(result_list)),
        no_matches_found=counter_false,
        no_matches_found_percent=percent(counter_false, len(result_list)),
        match_execution_time=round(time.time() - end_time, 2),
        timestamp=datetime.now(),
    )

    return DATABASE.select_all_with_analytics_images(analytics_image[1])


if __name__ == "__main__":
    pass
