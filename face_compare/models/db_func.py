import os
import sys

import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
from db_model import Faces, Links, create_tables
import numpy as np

USER = 'postgres'
PASSWORD = 'zebster1995'
HOST = 'localhost'
PORT = '5432'
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

    def add_new_link(self, link, connect_available=True):
        new_link = Links(link=link, connect_available=connect_available)

        self.session.add(new_link)
        self.session.commit()

        query = self.session.query(Links).where(Links.link == link).first()

        return query.id

    def add_new_face(self, link_id, face_array):

        # stmt = Links.update().where(Links.id == link_id).values(face_available=True)
        new_face = Faces(link_id=link_id, face=face_array)

        self.session.query(Links).where(Links.id == link_id).update({Links.face_available: True,
                                                                     Links.connect_available: True})
        self.session.add(new_face)
        self.session.commit()

    def get_face_from_link(self, link):

        query = self.session.query(Faces)
        query = query.join(Links)
        query = query.filter(Links.link == link).all()

        if query:
            list_ = [np.array([float(j) for j in i.face]) for i in query]

            return {'link_id': query[0].id,
                    'faces': list_}

    def get_all_faces(self):

        list_ = []

        query = self.session.query(Faces).order_by(Faces.link_id).all()
        if query:
            for element in query:
                dict_ = {
                    'link_id': element.link_id,
                    'faces': np.array([float(j) for j in element.face])
                }
                list_.append(dict_)

            return list_

    def get_all_links(self):

        query = self.session.query(Links.link).where(Links.connect_available == False)

        list_ = [element[0] for element in query]
        return list_

    def get_link_id(self, link):

        query = self.session.query(Links).where(Links.link == link,
                                                Links.connect_available == False).first()
        if query:
            return query.id
        return None

    def count_link_in_db(self, link):

        query = self.session.query(Links).filter(Links.link == link).all()

        if query:
            return True
        return False

    def none_connect(self, link):
        new_link = Links(link=link, connect_available=False)

        self.session.add(new_link)
        self.session.commit()

        query = self.session.query(Links).where(Links.link == link).first()

        return query.id

    def get_connect(self):

        query = self.session.query(Links).where(Links.connect_available == False)
        if query:

            return query

    def add_connect(self, link, face_available, connect_available):

        query = self.session.query(Links).where(Links.link == link).update({Links.face_available: face_available,
                                                                            Links.connect_available: connect_available})
        self.session.commit()
        if query:

            return True


if __name__ == '__main__':
    db_func = DataBaseORM()

    # with open('../attachments insta.txt') as file:
    #     links = file.readlines()
    #     links = [i.strip() for i in links]
    #
    # for link in links:
    #     if not db_func.count_link_in_db(link):
    #         db_func.add_new_link(link, connect_available=False)
