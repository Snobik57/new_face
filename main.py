import asyncio
import json
import time

from recognition_func import get_image_vector, compare_faces_, loop
from load_image import downloads_image


def _percent(num: int or float, total: int or float) -> float:
    # Функция для подсчета процента.
    result = (num * 100) / total
    return float("{:.2f}".format(result))


def gathering_information(image, urls: str):

    end_time = time.time()

    image_1 = loop.run_until_complete(get_image_vector(image))
    inter_list = asyncio.run(downloads_image(urls))
    result_list = loop.run_until_complete(compare_faces_(inter_list, image_1))

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
        'count_True': counter_true,
        'counter_True_percent': _percent(counter_true, len(result_list)),
        'count_False': counter_false,
        'counter_False_percent': _percent(counter_false, len(result_list)),
        'count_Not_found': counter_not_found,
        'counter_Not_found_percent': _percent(counter_not_found, len(result_list)),
        'time_to_end': time.time() - end_time,
        'results': result_list
    }

    with open(f'Result_async.json', 'w', encoding='utf8') as file_json:
        json.dump(result_dict, file_json, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    gathering_information('candidates/photo_410282.jpeg', 'attachments insta.txt')
