import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Links(Base):
    """Таблица со всеми ссылками на изображения из новостных статей"""
    __tablename__ = 'links'

    id = sq.Column(sq.Integer, primary_key=True)
    link = sq.Column(sq.VARCHAR(400))
    face_available = sq.Column(sq.Boolean, nullable=False, default=False)
    connect_available = sq.Column(sq.Boolean, nullable=False, default=False)


class Faces(Base):
    """Таблица, содержащая данные о лицах(вектора лиц) на изображениях из новостных статей"""
    __tablename__ = 'faces'

    id = sq.Column(sq.Integer, primary_key=True)
    link_id = sq.Column(sq.Integer, sq.ForeignKey('links.id'), nullable=False)
    face = sq.Column(sq.ARRAY(sq.Numeric))

    link = relationship('Links', backref='face')


class Analytics(Base):
    """Таблица с данными об аналитиках"""
    __tablename__ = 'analytics'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.VARCHAR(50), nullable=False)


class Images(Base):
    """Таблица содержащая данные об изображениях, загруженных аналитиками"""
    __tablename__ = 'images'

    id = sq.Column(sq.Integer, primary_key=True)
    id_analytics = sq.Column(sq.Integer, sq.ForeignKey('analytics.id'), nullable=False)
    image = sq.Column(sq.VARCHAR(255), nullable=False)
    inspected = sq.Column(sq.Boolean, default=False)

    analytic = relationship('Analytics', backref='image')


class SingleCompareFace(Base):
    """Таблица с данными о сравнении изображения аналитика с лицами(векторами лиц) с векторами из таблицы Faces"""
    __tablename__ = 'single_compare_face'

    id = sq.Column(sq.Integer, primary_key=True)
    image_id = sq.Column(sq.Integer, sq.ForeignKey('images.id'), nullable=False)
    face_id = sq.Column(sq.Integer, sq.ForeignKey('faces.id'), nullable=False)
    match_found = sq.Column(sq.Boolean)
    match_execution_time = sq.Column(sq.Numeric)

    image = relationship('Images', backref='single_compare_face')
    face = relationship('Faces', backref='single_compare_face')


class CompareFaces(Base):
    """Таблица с данными о всех сравнениях конкретного
    аналитического изображения со всеми векторами лиц из Таблицы Faces"""
    __tablename__ = 'compare_faces'

    id = sq.Column(sq.Integer, primary_key=True)
    image_id = sq.Column(sq.Integer, sq.ForeignKey('images.id'), nullable=False)
    matches_found = sq.Column(sq.Numeric)
    matches_found_percent = sq.Column(sq.Numeric)
    no_matches_found = sq.Column(sq.Numeric)
    no_matches_found_percent = sq.Column(sq.Numeric)
    match_execution_time = sq.Column(sq.Numeric)

    image = relationship('Images', backref='compare_faces')

    def __str__(self):
        return f"\nID: {self.id}\nImage_id: {self.image_id}\n" \
               f"matches_found: {self.matches_found}\n" \
               f"no_matches_found: {self.no_matches_found}\n" \
               f"match_execution_time: {self.match_execution_time}\n"


def create_tables(engine):
    Base.metadata.create_all(engine)
