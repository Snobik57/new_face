import asyncio

from data_generation import gathering_information
from engine_parse_image import downloads_image
from recognition_func import get_image_vector
from models.ch_db import DataBaseChORM
from time import sleep

DATABASE = DataBaseChORM()


def main():

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
            if image[0] not in images_embeddings_ids:
                print(f'[INFO] RECOGNITION: {image[0]}, {image[1]} ')
                embedding = get_image_vector(image[2])[0]
                DATABASE.insert_in_analytics_image_embedding(
                    image_id=image[0],
                    person_name=image[1],
                    embedding=embedding,
                )
        print(f"\n{'#' * 72}\n")

        sleep(2)

        # Сравнение всех изображений аналитиков со всеми найдеными лицами в БД
        # Если сравнение с изображением с аттачментом уже было проведено, то повторно не будет.

        for image in images_embeddings:

            print(f"[INFO] START: compare faces from {image[1]}")
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
