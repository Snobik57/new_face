import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Links(Base):
    __tablename__ = 'links'

    id = sq.Column(sq.Integer, primary_key=True)
    link = sq.Column(sq.VARCHAR(400))
    face_available = sq.Column(sq.Boolean, nullable=False, default=False)
    connect_available = sq.Column(sq.Boolean, nullable=False, default=False)


class Faces(Base):
    __tablename__ = 'faces'

    id = sq.Column(sq.Integer, primary_key=True)
    link_id = sq.Column(sq.Integer, sq.ForeignKey('links.id'), nullable=False)
    face = sq.Column(sq.ARRAY(sq.Numeric))

    link = relationship('Links', backref='face')


def create_tables(engine):
    Base.metadata.create_all(engine)
