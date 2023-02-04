from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
# from database import Base, engine
import sqlalchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists
from sqlalchemy.sql import func


SQLALCHEMY_DATABASE_URL = "postgresql://weatheruser:qwerty@127.0.0.1:5432/weatherdb"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



class Weather(Base):
    __tablename__ = "weather_info"

    id = Column(Integer, primary_key=True, index=True)
    city_id=Column(Integer, ForeignKey("city.cityid"))
    temp = Column(String, index=True)
    feels_like = Column(String)
    temp_min = Column(String, default=True)
    temp_max = Column(String, default='')
    pressure = Column(Integer, default=True)
    humidity= Column(Integer)
    sea_level=Column(Integer)
    grnd_level=Column(Integer)
    description = Column(String)

    cities = relationship("Cities", back_populates="weather_info")

class Cities(Base):
    __tablename__="city"
    cityid=Column(Integer,primary_key=True,unique=True,index=True)
    city_name=Column(String,unique=True)

    weather_info = relationship("Weather", back_populates="cities")


class Users(Base):
    __tablename__="user"
    id=Column(Integer,primary_key=True, index=True)
    email=Column(String,unique=True)
    password=Column(String)



def check_db_tables(engine=engine):
    print("checking if dabase is present or not")
    if database_exists(engine.url):
        print("database already present")

        print("creating tables if table is not present")
        Users.__table__.create(bind=engine, checkfirst=True)
        Cities.__table__.create(bind=engine, checkfirst=True)
        Weather.__table__.create(bind=engine, checkfirst=True)
        return True
    else:
        return False

# check_db_tables(engine)
 
