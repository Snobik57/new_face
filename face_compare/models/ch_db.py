import os

import numpy as np
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
        self.client = Client(host=HOST, user=USER, password=PASSWORD, port=PORT, database=NAME_DB)

    def create_table(self):
        self.client.execute("CREATE TABLE IF NOT EXISTS analytics ("
                            "analytics_name String,"
                            "image_path String"
                            ")"
                            "ENGINE = MergeTree()"
                            "ORDER BY (analytics_name, image_path);")

        self.client.execute('CREATE TABLE IF NOT EXISTS media_images ('
                            'attachment_id Int16,'
                            'face_available UInt8,'
                            'connect_available UInt8,'
                            'embedding Array(Float64),'
                            "created_at DateTime('Etc/GMT+6')"
                            ')'
                            'ENGINE = MergeTree()'
                            'ORDER BY (connect_available, attachment_id, face_available);')

        self.client.execute('CREATE TABLE IF NOT EXISTS analytics_images ('
                            'analytics_name String,'
                            'image_path String,'
                            'image_embedding Array(Float64),'
                            'inspected UInt8,'
                            "matches_found Int16,"
                            "matches_found_percent Float64,"
                            "no_matches_found Int16,"
                            "no_matches_found_percent Float64,"
                            "match_execution_time Float64,"
                            "created_at DateTime('Etc/GMT+6')"
                            ')'
                            'ENGINE = MergeTree()'
                            'ORDER BY (inspected, analytics_name);')

        self.client.execute("CREATE TABLE IF NOT EXISTS compare_faces ("
                            "analytics_name String,"
                            "image_path String,"
                            "attachment_id Int16,"
                            "match_found UInt8,"
                            "match_execution_time Float64,"
                            "created_at DateTime('Etc/GMT+6')"
                            ")"
                            "ENGINE = MergeTree()"
                            "ORDER BY (match_found, analytics_name, attachment_id);")

    def insert_in_media_images(self, attachment_id: int,
                               face_available: int,
                               connect_available: int,
                               embedding: ndarray,
                               timestamp: datetime):
        self.client.execute("INSERT INTO media_images (*) VALUES",
                            [{
                                'attachment_id': attachment_id,
                                'face_available': face_available,
                                'connect_available': connect_available,
                                'embedding': embedding,
                                'created_at': timestamp,
                            }])

    def insert_in_compare_faces(self,
                                analytics_name: str,
                                image_path: str,
                                attachment_id: int,
                                match_found: int,
                                match_execution_time: float,
                                timestamp: datetime):
        self.client.execute("INSERT INTO compare_faces (*) VALUES",
                            [{
                                'analytics_name': analytics_name,
                                'image_path': image_path,
                                'attachment_id': attachment_id,
                                'match_found': match_found,
                                'match_execution_time': match_execution_time,
                                'created_at': timestamp,
                            }])

    def insert_in_analytics_images(self,
                                   analytics_name: str,
                                   image_path: str,
                                   image_embedding: ndarray,
                                   inspected: int,
                                   matches_found: int,
                                   matches_found_percent: float,
                                   no_matches_found: int,
                                   no_matches_found_percent: float,
                                   match_execution_time: float,
                                   timestamp: datetime):
        self.client.execute("INSERT INTO analytics_images (*) VALUES",
                            [{
                                'analytics_name': analytics_name,
                                'image_embedding': image_embedding,
                                'inspected': inspected,
                                'image_path': image_path,
                                'matches_found': matches_found,
                                'matches_found_percent': matches_found_percent,
                                'no_matches_found': no_matches_found,
                                'no_matches_found_percent': no_matches_found_percent,
                                'match_execution_time': match_execution_time,
                                'created_at': timestamp,
                            }])

    def select_all_with_media_images(self):
        """Возвращает список всех массивов векторов из таблицы media_images"""

        query = self.client.execute(
            "SELECT (*) FROM media_images"
        )

        list_ = []

        if query:
            for element in query:
                if element[3]:
                    dict_ = {
                        'link_id': element[0],
                        'faces': np.array([float(j) for j in element[3]])
                    }
                    list_.append(dict_)

            return list_

    def select_all_with_analytics_images(self, image_path):
        """Возвращает результаты сравнения изображения со всеми векторами лиц из таблицы attachments"""

        query = self.client.execute(
            "SELECT analytics_name,"
                     "image_path,"
                     "matches_found,"
                     "matches_found_percent,"
                     "no_matches_found,"
                     "no_matches_found_percent,"
                     "match_execution_time "
            "FROM analytics_images "
            f"WHERE image_path == '{image_path}'"
        )
        return query[0]

    def select_result_faces_compare_faces(self, image_path):
        """Возвращает данные о всех сравнениях из таблицы compare_faces"""

        query = self.client.execute(
            f"SELECT (*) FROM compare_faces WHERE image_path == '{image_path}'"
        )
        return query

    def select_id_with_media_images(self):
        """Возвращает id всех ссылок из таблицы attachments"""

        query = self.client.execute(
            "SELECT attachment_id FROM media_images"
        )
        query = [i[0] for i in query]
        return query

    def select_all_attachments(self):
        """Возвращает элементы из таблицы attachments"""

        query_media_images = self.client.execute(
            "SELECT attachment_id FROM media_images"
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
        """Инспектирует таблицу analytics на наличие новых изображений в таблице"""

        query_analytics_image = self.client.execute(
            "SELECT image_path FROM analytics_images"
        )
        query_analytics_image = [i[0] for i in query_analytics_image]
        query_analytics = self.client.execute(
            "SELECT (*) FROM analytics"
        )
        list_ = []
        for image in query_analytics:
            if image[1] not in query_analytics_image:
                list_.append(image)

        return list_


if __name__ == "__main__":
    DATABASE = DataBaseChORM()
    DATABASE.create_table()
