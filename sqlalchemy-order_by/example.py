from sqlalchemy import create_engine, Column, Integer, desc, asc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///:memory:', echo=True)

Base = declarative_base()


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    age = Column(Integer)

    def __repr__(self):
        return f'Person<age={self.age}>'


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

session.add(Person(age=19))
session.add(Person(age=21))
session.add(Person(age=25))

session.commit()
