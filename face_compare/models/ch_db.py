import os
from pprint import pprint

import numpy as np
import pytz
from dotenv import load_dotenv
from numpy import ndarray

from clickhouse_driver import Client
from datetime import datetime

load_dotenv()

USER = os.getenv('user')
PASSWORD = os.getenv('password')
HOST = os.getenv('host')
PORT = os.getenv('port')
NAME_DB = os.getenv('database')


class DataBaseChORM:
    """Класс для работы с БД"""

    def __init__(self):
        self.client = Client(user=USER, password=PASSWORD, host=HOST, port=PORT, database=NAME_DB)

    def create_table(self):

        self.client.execute("CREATE TABLE IF NOT EXISTS attachments ("
                            "id Int16, "
                            "link String, "
                            "created_at DateTime('Etc/GMT+6')"
                            ")"
                            "ENGINE = MergeTree()"
                            "ORDER BY (created_at, id);")

        self.client.execute("CREATE TABLE IF NOT EXISTS analytics_images ("
                            "id Int16, "
                            "person_name String, "
                            "image_path String, "
                            "created_at DateTime('Etc/GMT+6')"
                            ")"
                            "ENGINE = MergeTree()"
                            "ORDER BY (id, created_at, person_name);")

        self.client.execute("CREATE TABLE IF NOT EXISTS analytics_image_embedding ("
                            "image_id Int16, "
                            "person_name String, "
                            "embedding Array(Float64)"
                            ")"
                            "ENGINE = MergeTree()"
                            "ORDER BY (image_id);")

        self.client.execute('CREATE TABLE IF NOT EXISTS attachments_embedding ('
                            'attachment_id Int16,'
                            'face_available UInt8,'
                            'connect_available UInt8,'
                            'embedding Array(Float64),'
                            "created_at DateTime('Etc/GMT+6')"
                            ')'
                            'ENGINE = MergeTree()'
                            'ORDER BY (created_at, face_available, connect_available);')

        self.client.execute('CREATE TABLE IF NOT EXISTS result ('
                            'image_id Int16,'
                            "person_name String, "
                            'inspected UInt8,'
                            "attachments_ids Array(Int16),"
                            "matches_found Int16,"
                            "matches_found_percent Float64,"
                            "no_matches_found Int16,"
                            "no_matches_found_percent Float64,"
                            "match_execution_time Float64,"
                            "created_at DateTime('Etc/GMT+6')"
                            ')'
                            'ENGINE = MergeTree()'
                            'ORDER BY (created_at, image_id);')

        self.client.execute("CREATE TABLE IF NOT EXISTS compare_faces ("
                            "image_id Int16,"
                            "attachment_id Int16,"
                            "match_found UInt8,"
                            "match_execution_time Float64,"
                            "created_at DateTime('Etc/GMT+6')"
                            ")"
                            "ENGINE = MergeTree()"
                            "ORDER BY (created_at, image_id, match_found);")


    def insert_in_attachments_embedding(self, attachment_id: int,
                                              face_available: int,
                                              connect_available: int,
                                              embedding: ndarray,
                                              timestamp: datetime):
        self.client.execute("INSERT INTO attachments_embedding (*) VALUES",
                            [{
                                'attachment_id': attachment_id,
                                'face_available': face_available,
                                'connect_available': connect_available,
                                'embedding': embedding,
                                'created_at': timestamp,
                            }])

    def insert_in_compare_faces(self,
                                image_id: int,
                                attachment_id: int,
                                match_found: int,
                                match_execution_time: float,
                                created_at: datetime):
        self.client.execute("INSERT INTO compare_faces (*) VALUES",
                            [{
                                'image_id': image_id,
                                'attachment_id': attachment_id,
                                'match_found': match_found,
                                'match_execution_time': match_execution_time,
                                'created_at': created_at,
                            }])

    def insert_in_analytics_image_embedding(self,
                                            image_id: int,
                                            person_name: str,
                                            embedding: ndarray,
                                            ):
        self.client.execute("INSERT INTO analytics_image_embedding (*) VALUES",
                            [{
                                'image_id': image_id,
                                'person_name': person_name,
                                'embedding': embedding,
                            }]
                            )

    def insert_in_result(self, image_id: int,
                               inspected: int,
                               person_name: str,
                               attachments_ids: list,
                               matches_found: int,
                               matches_found_percent: float,
                               no_matches_found: int,
                               no_matches_found_percent: float,
                               match_execution_time: float,
                               created_at: datetime):
        self.client.execute("INSERT INTO result (*) VALUES",
                            [{
                                'image_id': image_id,
                                'person_name': person_name,
                                'inspected': inspected,
                                'attachments_ids': attachments_ids,
                                'matches_found': matches_found,
                                'matches_found_percent': matches_found_percent,
                                'no_matches_found': no_matches_found,
                                'no_matches_found_percent': no_matches_found_percent,
                                'match_execution_time': match_execution_time,
                                'created_at': created_at,
                            }])
    def select_all_analytics_images(self):
        """Возвращает список всех фотографий для аналитики."""
        query = self.client.execute(
            "SELECT (*) "
            "FROM analytics_images;"
        )
        return query

    def select_all_analytics_images_embeddings(self):
        """Возвращает список всех Эмбеддингов с фотографий для аналитики."""
        query = self.client.execute(
            "SELECT (*) "
            "FROM analytics_image_embedding;"
        )
        return query

    def select_all_with_attachments_embedding(self, image_id: int):
        """Возвращает список всех массивов векторов из таблицы attachments_embedding"""

        query_in_compare_faces = self.client.execute(
            "SELECT attachment_id "
            "FROM compare_faces "
            f"WHERE image_id = {image_id};"
        )

        query = self.client.execute(
            "SELECT (*) "
            "FROM attachments_embedding "
            "WHERE face_available == 1;"
        )

        list_ = []

        for element in query:
            if element[3] and element[0] not in [i[0] for i in query_in_compare_faces]:
                dict_ = {
                    'link_id': element[0],
                    'faces': np.array([float(j) for j in element[3]])
                }
                list_.append(dict_)

        return list_

    def select_all_with_result(self, image_id):
        """Возвращает результаты сравнения изображения со всеми векторами лиц из таблицы attachments"""

        query = self.client.execute(
            "SELECT image_id, "
                   "person_name, "
                   "matches_found, "
                   "attachments_ids, "
                   "matches_found_percent, "
                   "no_matches_found, "
                   "no_matches_found_percent, "
                   "match_execution_time, "
                   "created_at "
            "FROM result "
            f"WHERE image_id == '{image_id}'"
        )
        return query[0]

    def select_result_faces_compare_faces(self, image_id):
        """Возвращает данные о всех сравнениях из таблицы compare_faces"""

        query = self.client.execute(
            f"SELECT (*) "
            f"FROM compare_faces "
            f"WHERE (image_id == '{image_id}');"
        )
        return query

    def select_id_with_attachments_embedding(self):
        """Возвращает id всех ссылок из таблицы attachments"""

        query = self.client.execute(
            "SELECT attachment_id FROM attachments_embedding"
        )
        query = [i[0] for i in query]
        return query

    def select_all_attachments(self):
        """Возвращает элементы из таблицы attachments"""

        query_media_images = self.client.execute(
            "SELECT attachment_id FROM attachments_embedding"
        )
        query_media_images = [i[0] for i in query_media_images]

# TODO: Тут необходимо изменить таблицу, из которой беруться данные.
        query = self.client.execute(
            "SELECT id, link FROM attachments"
        )

        list_ = []

        for element in query:
            if element[0] not in query_media_images:
                list_.append(element)

        return list_

    def select_all_images_in_compare_face(self):
        """Возвращает все название изображений из таблицы compare_face"""

        query = self.client.execute(
            "SELECT image_path FROM compare_face"
        )
        query = [i[0] for i in query]
        return query

    def select_attachments_match_found(self, image_path):
        """Возвращает id аттачментов на которых были найдены совпадения"""

        query = self.client.execute(
            f"SELECT attachment_id FROM compare_faces WHERE match_found == 1 AND image_path == '{image_path}'"
        )

        return query

    def database_inspection(self):
        """Инспектирует таблицу analytics_image на наличие новых изображений в таблице"""

        query_analytics = self.client.execute(
            "SELECT (*) FROM analytics_image"
        )

        return query_analytics

    def drop_table(self, name: str):
        """Удаляет таблицы из БД"""

        query = self.client.execute(
            f"DROP TABLE IF EXISTS {name}"
        )


if __name__ == "__main__":
    DATABASE = DataBaseChORM()
    DATABASE.create_table()

    # pprint(DATABASE.select_all_with_attachments_embedding(1))

    # with open('attachments insta.txt') as file:
    #     list_ = [i.strip() for i in file.readlines()]
    #
    # for i, link in enumerate(list_, start=1):
    #     DATABASE.client.execute(
    #         "INSERT INTO attachments (*) VALUES",
    #         [{'id': i, 'link': link, 'created_at': datetime.now()}]
    #     )
