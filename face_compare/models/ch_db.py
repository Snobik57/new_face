import os
import numpy as np

from typing import List
from dotenv import load_dotenv
from numpy import ndarray
from clickhouse_driver import Client
from datetime import datetime


load_dotenv()


class DataBaseChORM:
    """Класс для работы с БД"""

    def __init__(self, client=None):
        if client:
            self.client_recognition = client
        else:
            self.client_recognition = Client(
                user=os.getenv('user'),
                password=os.getenv('password'),
                host=os.getenv('host'),
                port=os.getenv('port'),
                database='recognition',
            )

            # TODO: Тут необходимо изменить БД, из которой беруться данные.
            self.client_imas = Client(
                user=os.getenv('user'),
                password=os.getenv('password'),
                host=os.getenv('host'),
                port=os.getenv('port'),
                database='local_imas',
            )

    def create_table(self) -> List[tuple]:
        """Создает таблицы в БД"""

        self.client_recognition.execute("CREATE TABLE IF NOT EXISTS analytics_images ("
                                        "id Int16, "
                                        "person_name String, "
                                        "image_path String,"
                                        "s_date Date, "
                                        "f_date Date, "
                                        "appender_status Int8, "
                                        "user_id Int16, "
                                        "created_at DateTime('Etc/GMT+6')"
                                        ")"
                                        "ENGINE = MergeTree()"
                                        "ORDER BY (id, created_at, person_name);")

        self.client_recognition.execute("CREATE TABLE IF NOT EXISTS analytics_image_embedding ("
                                        "image_id Int16, "
                                        "person_name String, "
                                        "embedding Array(Float64)"
                                        ")"
                                        "ENGINE = MergeTree()"
                                        "ORDER BY (image_id);")

        self.client_recognition.execute('CREATE TABLE IF NOT EXISTS attachments_embedding ('
                                        'attachment_id Int64,'
                                        'face_available UInt8,'
                                        'connect_available UInt8,'
                                        'embedding Array(Float64),'
                                        "created_at DateTime('Etc/GMT+6')"
                                        ')'
                                        'ENGINE = MergeTree()'
                                        'ORDER BY (created_at, face_available, connect_available);')

        # self.client_recognition.execute('CREATE TABLE IF NOT EXISTS result ('
        #                                 'image_id Int16,'
        #                                 "person_name String, "
        #                                 'inspected UInt8,'
        #                                 "attachments_ids Array(Int64),"
        #                                 "matches_found Int16,"
        #                                 "matches_found_percent Float64,"
        #                                 "no_matches_found Int16,"
        #                                 "no_matches_found_percent Float64,"
        #                                 "match_execution_time Float64,"
        #                                 "created_at DateTime('Etc/GMT+6')"
        #                                 ')'
        #                                 'ENGINE = MergeTree()'
        #                                 'ORDER BY (created_at, image_id);')

        self.client_recognition.execute("CREATE TABLE IF NOT EXISTS compare_faces ("
                                        "image_id Int16,"
                                        "attachment_id Int64,"
                                        "match_found UInt8,"
                                        "match_execution_time Float64,"
                                        "created_at DateTime('Etc/GMT+6')"
                                        ")"
                                        "ENGINE = MergeTree()"
                                        "ORDER BY (created_at, image_id, match_found);")

        result = self.client_recognition.execute("""
        SHOW TABLES;
        """)

        return result

    def insert_in_attachments_embedding(self,
                                        attachment_id: int,
                                        face_available: int,
                                        connect_available: int,
                                        embedding: ndarray,
                                        timestamp: datetime) -> int:
        """Добавляет данные в таблицу attachments_embedding"""

        result = self.client_recognition.execute("INSERT INTO attachments_embedding (*) VALUES",
                                                 [{
                                                     'attachment_id': attachment_id,
                                                     'face_available': face_available,
                                                     'connect_available': connect_available,
                                                     'embedding': embedding,
                                                     'created_at': timestamp,
                                                 }])
        return result

    def insert_in_compare_faces(self,
                                image_id: int,
                                attachment_id: int,
                                match_found: int,
                                match_execution_time: float,
                                created_at: datetime) -> int:
        """Добавляет данные в таблицу compare_faces"""

        result = self.client_recognition.execute("INSERT INTO compare_faces (*) VALUES",
                                                 [{
                                                    'image_id': image_id,
                                                    'attachment_id': attachment_id,
                                                    'match_found': match_found,
                                                    'match_execution_time': match_execution_time,
                                                    'created_at': created_at,
                                                 }])

        return result

    def insert_in_analytics_image_embedding(self,
                                            image_id: int,
                                            person_name: str,
                                            embedding: ndarray,
                                            ) -> int:
        """Добавляет данные в таблицу analytics_image_embedding"""

        result = self.client_recognition.execute("INSERT INTO analytics_image_embedding (*) VALUES",
                                                 [{
                                                    'image_id': image_id,
                                                    'person_name': person_name,
                                                    'embedding': embedding,
                                                 }])

        return result

    def insert_in_result(self,
                         image_id: int,
                         inspected: int,
                         person_name: str,
                         attachments_ids: list,
                         matches_found: int,
                         matches_found_percent: float,
                         no_matches_found: int,
                         no_matches_found_percent: float,
                         match_execution_time: float,
                         created_at: datetime) -> int:
        """Добавляет данные в таблицу result"""

        result = self.client_recognition.execute("INSERT INTO result (*) VALUES",
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

        return result

    def select_all_analytics_images(self) -> list:
        """Возвращает список всех фотографий для аналитики."""

        query = self.client_recognition.execute(
            "SELECT (*) "
            "FROM analytics_images;"
        )
        return query

    def select_all_analytics_images_embeddings(self) -> tuple:
        """Возвращает список всех Эмбеддингов с фотографий для аналитики."""

        query = self.client_recognition.execute(
            "SELECT (*) "
            "FROM analytics_image_embedding;"
        )
        return query

    def select_all_with_attachments_embedding(self, image_id: int) -> list:
        """
        Возвращает список массивов векторов из таблицы attachments_embedding,
        которые не прошли сравнения с конкретным аналитическим изображением.

        :param image_id: ID аналитического изображения
        """

        query_in_compare_faces = self.client_recognition.execute(
            "SELECT attachment_id "
            "FROM compare_faces "
            f"WHERE image_id = {image_id};"
        )

        query = self.client_recognition.execute(
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

    def select_all_with_result(self, image_id: int) -> tuple:
        """Возвращает результаты сравнения изображения со всеми векторами лиц из таблицы result"""

        query = self.client_recognition.execute(
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

    def select_result_faces_compare_faces(self, image_id: int) -> tuple:
        """
        Возвращает данные о всех сравнениях из таблицы compare_faces
        для конкретного аналитического изображения
        """

        query = self.client_recognition.execute(
            f"SELECT (*) "
            f"FROM compare_faces "
            f"WHERE (image_id == '{image_id}');"
        )
        return query

    def select_id_with_attachments_embedding(self) -> List[int]:
        """Возвращает id всех ссылок из таблицы attachments_embedding"""

        query = self.client_recognition.execute(
            "SELECT attachment_id FROM attachments_embedding"
        )
        query = [i[0] for i in query]
        return query

    def select_all_attachments(self, type_attachment: int) -> List[tuple]:
        """
        Возвращает объекты из таблицы attachments,
        которые не были добавлены в таблицу attachments_embedding
        """

        query_media_images = self.client_recognition.execute(
            "SELECT attachment_id FROM attachments_embedding"
        )
        query_media_images = [i[0] for i in query_media_images]

        query = self.client_imas.execute(
            f"SELECT id, attachment "
            f"FROM attachments "
            f"WHERE type = {type_attachment}"
        )

        list_ = []

        for element in query:
            if element[0] not in query_media_images:
                list_.append(element)

        return list_

    def select_all_images_in_compare_face(self) -> List[int]:
        """Возвращает все пути изображений из таблицы compare_face"""

        query = self.client_recognition.execute(
            "SELECT image_id FROM compare_faces"
        )
        query = [i[0] for i in query]
        return query

    def select_attachments_match_found(self, image_id: int) -> tuple:
        """Возвращает id аттачментов на которых были найдены совпадения"""

        query = self.client_recognition.execute(
            f"SELECT attachment_id FROM compare_faces WHERE match_found == 1 AND image_id == '{image_id}'"
        )

        return query

    def database_inspection(self) -> tuple:
        """Инспектирует таблицу analytics_image на наличие новых изображений в таблице"""

        query_analytics = self.client_recognition.execute(
            "SELECT (*) FROM analytics_images"
        )

        return query_analytics

    def drop_table(self, name: str) -> int:
        """Удаляет таблицы из БД"""

        query = self.client_recognition.execute(
            f"DROP TABLE IF EXISTS {name}"
        )

        return query


if __name__ == "__main__":
    DATABASE = DataBaseChORM()
    DATABASE.create_table()
