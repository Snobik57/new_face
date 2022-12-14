import time
import numpy as np
from datetime import datetime

from models.ch_db import DataBaseChORM
from recognition_func import get_image_embedding, compare_faces_, percent


DATABASE = DataBaseChORM()


def gathering_information(analytics_image: tuple):
    """
    Сравнивает эмбеддинг изображения с данными из БД.
    Записывает результат в БД в таблицу analytics_images

    :param analytics_image: id изображения из БД

    :return: Возвращает список данных по полученному изображению из analytics_images
    """

    # end_time = time.time()

    image_embedding = analytics_image[2]
    attachments_embeddings = DATABASE.select_all_with_attachments_embedding(image_id=analytics_image[0])
    result = compare_faces_(attachments_embeddings, image_embedding, analytics_image)

    # attachment_list = np.array([i[1] for i in result['match_found']])
    # count_matches = len(result['match_found'])
    # count_not_matches = len(result['match_not_found'])
    # matches_found_percent = percent(count_matches, count_matches + count_not_matches)
    # no_matches_found_percent = percent(count_not_matches, count_matches + count_not_matches)
    #
    # DATABASE.insert_in_result(
    #     image_id=analytics_image[0],
    #     person_name=analytics_image[1],
    #     inspected=1,
    #     attachments_ids=attachment_list,
    #     matches_found=count_matches,
    #     matches_found_percent=matches_found_percent,
    #     no_matches_found=count_not_matches,
    #     no_matches_found_percent=no_matches_found_percent,
    #     match_execution_time=round(time.time() - end_time, 2),
    #     created_at=datetime.now(),
    # )
    #
    # return DATABASE.select_all_with_result(analytics_image[0])
