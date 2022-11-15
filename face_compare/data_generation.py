import time

from recognition_func import get_image_vector, compare_faces_, percent
from models.db_func import DataBaseORM


DATABASE = DataBaseORM()


def gathering_information(image_id: int, image: str):
    """
    Сравнивает эмбеддинг изображения с данными из БД.
    Записывает результат в БД (модель CompareFaces)

    :param image_id: id изображения из БД
    :param image: путь изображения из БД.
    :return: объект модели CompareFaces
    """

    end_time = time.time()
    base_image = get_image_vector(image)

    inter_list = DATABASE.get_all_faces()
    result_list = compare_faces_(inter_list, base_image, image_id)

    counter_true = 0
    counter_false = 0

    for element in result_list:
        if element.match_found is True:
            counter_true += 1
        elif element.match_found is False:
            counter_false += 1

    DATABASE.add_new_multiple_compare(
        image_id=image_id,
        matches_found=counter_true,
        matches_found_percent=percent(counter_true, len(result_list)),
        no_matches_found=counter_false,
        no_matches_found_percent=percent(counter_false, len(result_list)),
        match_execution_time=round(time.time() - end_time, 2),
    )

    return DATABASE.get_all_compare_from_image(image_id)


if __name__ == "__main__":
    pass
