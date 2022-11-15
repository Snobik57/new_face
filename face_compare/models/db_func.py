import os
import sys
from pprint import pprint

import sqlalchemy as sq
import numpy as np

from numpy import ndarray
from sqlalchemy.orm import sessionmaker
from typing import List, Union
from dotenv import load_dotenv

from db_model import Faces, Links, SingleCompareFace, CompareFaces, create_tables, Images

load_dotenv()

USER = os.getenv('USER_')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
name_db = 'new_face'

DSN = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{name_db}'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


class DataBaseORM:

    def __init__(self):
        engine = sq.create_engine(DSN)

        create_tables(engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()

    def add_new_link(self, link: str, connect_available: bool = True) -> int:
        """Добавляет ссылку в Модель Links"""
        if link[:4] == 'http':
            new_link = Links(link=link, connect_available=connect_available)

            self.session.add(new_link)
            self.session.commit()

            query = self.session.query(Links).where(Links.link == link).first()

            return query.id
        else:
            raise TypeError("attr:'link' mast start with <http>")

    def add_new_face(self, link_id: int or str, face_array: ndarray) -> bool:
        """Добавляет массив векторов в модель Faces по Links.id"""
        new_face = Faces(link_id=link_id, face=face_array)

        query = self.session.query(Links).where(Links.id == link_id).update({Links.face_available: True,
                                                                             Links.connect_available: True})
        self.session.add(new_face)
        self.session.commit()
        if query:
            return True
        return False

    def add_new_compare(self, image_id, face_id, match_found, match_execution_time):
        """Добавляет данные о сравнении аналитического изображения и эмбеддинга из БД"""
        new_compare = SingleCompareFace(
            image_id=image_id,
            face_id=face_id,
            match_found=match_found,
            match_execution_time=match_execution_time
        )
        self.session.add(new_compare)
        self.session.commit()

    def add_new_multiple_compare(
            self,
            image_id,
            matches_found,
            matches_found_percent,
            no_matches_found,
            no_matches_found_percent,
            match_execution_time
    ):
        """Добавляет данные о всех сравнениях аналитического изображения"""
        new_compare = CompareFaces(
            image_id=image_id,
            matches_found=matches_found,
            matches_found_percent=matches_found_percent,
            no_matches_found=no_matches_found,
            no_matches_found_percent=no_matches_found_percent,
            match_execution_time=match_execution_time
        )
        self.session.add(new_compare)
        self.session.commit()

    def get_all_compare_from_image(self, image_id):
        """Возвращает данные о всех сравнениях аналитического изображения в виде объекта модели CompareFaces"""
        query = self.session.query(CompareFaces).where(CompareFaces.image_id == image_id).all()
        if query:
            return query[0]

    def get_compare_from_image(self, image_id):
        """Возвращает данные о всех сравнениях аналитического изображения в виде объектов модели SingleCompareFace"""
        query = self.session.query(SingleCompareFace).where(SingleCompareFace.image_id == image_id).all()
        if query:
            return query

    def get_face_from_link(self, link: str) -> dict:
        """Возвращает массив векторов из модели Faces по указанной ссылке из модели Links"""
        query = self.session.query(Faces)
        query = query.join(Links)
        query = query.filter(Links.link == link).all()

        if query:
            list_ = [np.array([float(j) for j in i.face]) for i in query]

            return {'link_id': query[0].id,
                    'faces': list_}

    def get_all_faces(self) -> List[dict]:
        """Возвращает список всех массивов векторов из модели Faces"""
        list_ = []

        query = self.session.query(Faces).order_by(Faces.link_id).all()
        if query:
            for element in query:
                dict_ = {
                    'face_id': element.id,
                    'link_id': element.link_id,
                    'faces': np.array([float(j) for j in element.face])
                }
                list_.append(dict_)

            return list_

    def get_all_links(self) -> List[str]:
        """Возвращает список со всеми ссылками хранящиеся в модели Links"""
        query = self.session.query(Links.link).where(Links.connect_available == False)

        list_ = [element[0] for element in query]
        return list_

    def get_link_id(self, link: str) -> Union[int or str, None]:
        """Возвращает PK(id) из модели Links по указанной ссылке"""
        query = self.session.query(Links).where(Links.link == link,
                                                Links.connect_available == False).first()
        if query:
            return query.id
        return None

    def count_link_in_db(self, link: str) -> bool:
        """Возвращает булево-значение о нахождении ссылки в модели Links"""
        query = self.session.query(Links).filter(Links.link == link).all()

        if query:
            return True
        return False

    def add_connect(self, link: str, face_available: bool, connect_available: bool) -> bool:
        """Добавляет новое значение Links.face_available и Links.connect_available для ссылки из модели Links"""
        query = self.session.query(Links).where(Links.link == link).update({Links.face_available: face_available,
                                                                            Links.connect_available: connect_available})
        self.session.commit()
        if query:

            return True

    def add_inspect(self, image_id):
        """Обновляет запись в модели Images изменяя значение inspected на True"""
        query = self.session.query(Images).where(Images.id == image_id).update({Images.inspected: True})

        self.session.commit()
        if query:
            return True

    def database_inspection(self):
        """Возвращает все аналитические изображения, которые ещё не были инспектированы инспектором"""
        query = self.session.query(Images).where(Images.inspected == False).all()

        if query:
            return query
        return []

    def close(self):
        self.session.close()


if __name__ == '__main__':
    DATABASE = DataBaseORM()
    pprint(DATABASE.get_all_faces())

