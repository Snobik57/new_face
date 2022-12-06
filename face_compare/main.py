import asyncio

from data_generation import gathering_information
from parse_attachments import downloads_image
from recognition_func import get_image_embedding
from models.ch_db import DataBaseChORM
from time import sleep

DATABASE = DataBaseChORM()


def main():
    """
    Основная функция приложения. Разделена на 3 составные части:

    Забирает аттачменты из внешней БД, скачивает фотографии,
    распознает на них лица и заносит данные в таблицу attachments_embedding.
    Если аттачмент уже хранится в таблице, то скачивания не произойдет.

    Забирает пути к фотографиям для аналитики из БД,
    распознает на них лица и заносит данные в таблицу analytics_image_embedding.
    Если ембеддинг уже хранится в БД, то распознавания не произойдет.

    Сравнивает все эмбеддинги аттачментов и фотографий для аналитики.
    Записывает результат в БД
    Если сравнение с изображением с аттачментом уже было проведено, то повторно не будет.
    """

    while True:

        # Скрапинг аттачментов из БД с добавлением эмбеддингов в БД

        print('[INFO] START: face recognition on new attachments ')
        asyncio.run(downloads_image())
        print('[INFO] FINISH: face recognition')
        print(f"\n{'#' * 72}\n")

        sleep(2)

        # Забираем все аналитические эмбеддинги из БД
        # Если существуют новые изображения, то обрабатываем и добавляем в БД

        images = DATABASE.select_all_analytics_images()
        images_embeddings = DATABASE.select_all_analytics_images_embeddings()
        images_embeddings_ids = [i[0] for i in images_embeddings] if images_embeddings else []

        for image in images:

            image_id = image[0]
            person_name = image[1]

            if image_id not in images_embeddings_ids:
                print(f'[INFO] RECOGNITION: {image_id}, {person_name} ')
                embedding = get_image_embedding(image[2])[0]
                DATABASE.insert_in_analytics_image_embedding(
                    image_id=image_id,
                    person_name=person_name,
                    embedding=embedding,
                )
        print(f"\n{'#' * 72}\n")

        sleep(2)

        # Сравнение всех изображений аналитиков со всеми найдеными лицами в БД
        # Если сравнение с изображением с аттачментом уже было проведено, то повторно не будет.

        for image in images_embeddings:

            person_name = image[1]

            print(f"[INFO] START: compare faces from {person_name}")
            inform_with_compare = gathering_information(analytics_image=image)
            print(f"[INFO] ABOUT: the new image of analysts:\n{inform_with_compare}")
            print(f"\n{'#' * 72}\n")

            sleep(2)

        print('[INFO] RESTART: via')
        for _ in range(5, -1, -1):
            print(_)
            sleep(1)

if __name__ == "__main__":
    main()
