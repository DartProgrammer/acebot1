from sqlalchemy import (Column, Integer, String, BigInteger, Sequence, ForeignKey, TIMESTAMP, Boolean, Text)
from sqlalchemy import sql

from data.config import HOBBY_STRING_LENGTH
from utils.db_api.database import db


# Пользователи
class User(db.Model):
    __tablename__ = 'users'

    # id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(BigInteger, primary_key=True, unique=True)
    name = Column(String(100))
    username = Column(String(50))
    email = Column(String(50))
    language = Column(String(50))
    game1 = Column(String(50))
    game2 = Column(String(50))
    play_level = Column(String(50))
    cool_down = Column(Integer, default=0)
    age = Column(Integer)
    gender = Column(String(50))
    purpose = Column(String(50))
    who_search = Column(String(50))
    country = Column(String(50))
    city = Column(String(50))
    about_yourself = Column(String(500))
    hobby = Column(String(HOBBY_STRING_LENGTH))
    photo = Column(String(250))
    enable = Column(Boolean, default=True)
    complaint = Column(Integer, default=0)

    query: sql.Select

    def __repr__(self):
        return f"<User(id='{self.user_id}', name='{self.name}', username='{self.username}')>"


# Понравившиеся профили
class LikeProfiles(db.Model):
    __tablename__ = 'like_profiles'

    id = Column(Integer, Sequence('like_profiles_id_seq'), primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    like_profile_id = Column(BigInteger)
    timestamp = Column(TIMESTAMP)
    read = Column(Boolean, default=False)

    query: sql.Select

    def __repr__(self):
        return f"<LikeProfiles(id='{self.id}', user_id='{self.user_id}', like_profile_id='{self.like_profile_id}')>"


# Профили, написавшие сообщения
class SendMessageProfiles(db.Model):
    __tablename__ = 'send_message_profiles'

    id = Column(Integer, Sequence('send_message_profiles_id_seq'), primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    profile_id = Column(BigInteger)
    send_message_text = Column(Text)
    timestamp = Column(TIMESTAMP)
    read = Column(Boolean, default=False)

    query: sql.Select

    def __repr__(self):
        return f"<SendMessageProfiles(id='{self.id}', user_id='{self.user_id}', " \
               f"send_message_profile_id='{self.send_message_profile_id}')>"


# Жалобы на профили
class ComplaintProfiles(db.Model):
    __tablename__ = 'complaint_profiles'

    id = Column(Integer, Sequence('like_profiles_id_seq'), primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    complaint_profile_id = Column(BigInteger)
    reason_complaint = Column(String(50))
    timestamp = Column(TIMESTAMP)

    query: sql.Select

    def __repr__(self):
        return f"<ComplaintProfiles(id='{self.id}', user_id='{self.user_id}', " \
               f"complaint_profile_id='{self.complaint_profile_id}', reason_complaint='{self.reason_complaint}')>"


# Страны
class Country(db.Model):
    __tablename__ = 'country'

    id = Column(BigInteger, primary_key=True, nullable=False)
    name = Column(String(128), nullable=False)
    crt_date = Column(TIMESTAMP)

    query: sql.Select

    def __repr__(self):
        return f"<Country(id='{self.id}', name='{self.name}')>"


# Регионы
class Region(db.Model):
    __tablename__ = 'region'

    id = Column(BigInteger, primary_key=True, nullable=False)
    country_id = Column(BigInteger, ForeignKey('country.id'), nullable=False)
    name = Column(String(128), nullable=False)
    crt_date = Column(TIMESTAMP)

    query: sql.Select

    def __repr__(self):
        return f"<Region(id='{self.id}', name='{self.name}')>"


# Города
class City(db.Model):
    __tablename__ = 'city'

    id = Column(BigInteger, primary_key=True, nullable=False)
    region_id = Column(BigInteger, ForeignKey('region.id'), nullable=False)
    name = Column(String(128), nullable=False)
    crt_date = Column(TIMESTAMP)

    query: sql.Select

    def __repr__(self):
        return f"<City(id='{self.id}', name='{self.name}')>"
