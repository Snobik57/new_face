import json
import time

from recognition.recognition_func import get_image_vector, compare_faces_, percent
from models.db_func import DataBaseORM


DATABASE = DataBaseORM()


def gathering_information(image: str) -> None:
    """
    Сравнивает эмбеддинг изображения с данными из БД. Записывает результат в json

    :param image: имя или путь изображения.
    :return: None
    """

    end_time = time.time()
    base_image = get_image_vector(image)

    inter_list = DATABASE.get_all_faces()
    result_list = compare_faces_(inter_list, base_image)

    counter_true = 0
    counter_false = 0
    counter_not_found = 0

    for element in result_list:
        if element['result'] == 'True':
            counter_true += 1
        elif element['result'] == 'False':
            counter_false += 1
        elif element['result'] == 'Not found':
            counter_not_found += 1

    result_dict = {
        'base_image': image,
        'count_True': counter_true,
        'counter_True_percent': percent(counter_true, len(result_list)),
        'count_False': counter_false,
        'counter_False_percent': percent(counter_false, len(result_list)),
        'time_to_end': round(time.time() - end_time, 2),
        'results': result_list
    }

    name_file = image.split('/')[-1]

    with open(f'../Result_async_{name_file}.json', 'w', encoding='utf8') as file_json:
        json.dump(result_dict, file_json, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    gathering_information('candidates/photo_409345.jpeg')
