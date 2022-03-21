import datetime

from aiogram import types
from sqlalchemy import desc, or_

from utils.db_api.models import User, LikeProfiles, ComplaintProfiles, Country, City, Region, SendMessageProfiles


class DBCommands:

    # Получение пользователя
    async def get_user(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    # Получение всех пользователей
    async def get_users(self):
        users = await User.select('user_id').gino.all()
        return users

    # Добавление нового пользователя
    async def add_new_user(self, referral=None):
        user = types.User.get_current()
        old_user = await self.get_user(user.id)
        if old_user:
            return old_user
        new_user = User()
        new_user.user_id = user.id
        new_user.username = user.username
        new_user.full_name = user.full_name

        await new_user.create()
        return new_user

    # Изменение языка пользователя
    async def set_language(self, language):
        user_id = types.User.get_current().id
        user = await self.get_user(user_id)
        await user.update(language=language).apply()

    # Получение языка пользователя
    async def get_user_language(self, user_id):
        language = await User.select('language').where(User.user_id == int(user_id)).gino.scalar()
        return language

    # Добавление в БД профиля, которому поставили лайк
    async def add_like_profile(self, like_profile_id):
        user_id = types.User.get_current().id
        # old_like_profile = await self.get_user_like_profile(user_id, like_profile_id)
        # if old_like_profile:
        #     return old_like_profile
        new_like_profile = LikeProfiles()
        new_like_profile.user_id = user_id
        new_like_profile.like_profile_id = like_profile_id
        new_like_profile.timestamp = datetime.datetime.now()

        await new_like_profile.create()
        return new_like_profile

    # Получение всех профилей, которым пользователь поставил лайк
    async def get_user_like_profiles(self, user_id):
        like_profiles = await LikeProfiles.select('like_profile_id').where(LikeProfiles.user_id == user_id).gino.all()
        return like_profiles

    # Получение конкретного профиля, которому поставили лайк
    async def get_user_like_profile(self, user_id, like_profile_id):
        like_profile = await LikeProfiles.select('like_profile_id').where(LikeProfiles.user_id == user_id).where(
            LikeProfiles.like_profile_id == like_profile_id).gino.first()
        return like_profile

    # Получение всех профилей, которые поставили лайк
    async def get_users_liked_my_profile(self, user_id):
        # users_liked = await LikeProfiles, User.select().where(LikeProfiles.like_profile_id == user_id).gino.all()
        users_liked = await LikeProfiles.join(User).select().where(LikeProfiles.like_profile_id == user_id).where(
        LikeProfiles.read == False).gino.all()
        return users_liked

    # Получение первого профиля, который поставил лайк
    async def get_user_liked_my_profile(self, user_id):
        user_liked = await LikeProfiles.select('user_id').where(LikeProfiles.like_profile_id == user_id).order_by(
            desc('timestamp')).gino.first()
        return user_liked

    # Получение всех профилей, которые написали письмо
    async def get_users_send_message(self, user_id):
        users_send_message = await SendMessageProfiles.join(User).select().where(
            SendMessageProfiles.profile_id == user_id).where(SendMessageProfiles.read == False).gino.all()
        return users_send_message

    # Получение количества жалоб на пользователя
    async def get_user_complaints(self, user_id):
        complaints = await User.select('complaint').where(User.user_id == user_id).gino.scalar()
        return complaints

    # Добавление жалобы на профиль
    async def add_complaint_for_profile(self, complaint_profile_id, reason_complaint):
        user_id = types.User.get_current().id
        new_complaint_profile = ComplaintProfiles()
        new_complaint_profile.user_id = user_id
        new_complaint_profile.complaint_profile_id = complaint_profile_id
        new_complaint_profile.reason_complaint = reason_complaint
        new_complaint_profile.timestamp = datetime.datetime.now()

        await new_complaint_profile.create()
        return new_complaint_profile

    # Установка признака "Прочитано" для прочитанных сообщений пользователей, которые написали письмо
    async def setting_the_attribute_read(self, msg_id):
        message = await SendMessageProfiles.query.where(SendMessageProfiles.id == msg_id).gino.first()
        await message.update(read=True).apply()

    # Установка признака "Прочитано" для прочитанных сообщений пользователей, которые поставили лайк
    async def setting_the_attribute_read_like_profiles(self, msg_id):
        message = await LikeProfiles.query.where(LikeProfiles.id == msg_id).gino.first()
        await message.update(read=True).apply()

    # Получение страны
    async def get_country(self, country):
        country = await Country.query.where(Country.name == country).gino.first()
        return country

    # Получение всех стран
    async def get_all_countries(self):
        countries = await Country.select('name').gino.all()
        return countries

    # Получение всех регионов
    async def get_all_regions(self, country):
        country_id = await Country.select('id').where(Country.name == country).gino.scalar()
        regions = await Region.select('name').where(Region.country_id == country_id).gino.all()
        return regions

    # Получение всех городов
    async def get_all_cities(self, region):
        region_id = await Region.select('id').where(Region.name == region).gino.scalar()
        cities = await City.select('name').where(City.region_id == region_id).gino.all()
        return cities


class FindUsers:

    # Функция поиска пользователей
    async def find_user_to_purpose(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        purpose = user.purpose
        who_search = user.who_search

        if who_search in ['Девушек', 'Girls']:
            gender = ['Девушка', 'Girl']
        elif who_search in ['Парней', 'Guys']:
            gender = ['Парень', 'Guy']
        else:
            gender = ['Девушка', 'Girl', 'Парень', 'Guy']

        age = user.age
        game1 = user.game1
        game2 = user.game2
        country = user.country
        city = user.city

        # Ищем анкеты, где цель поиска "Просто поиграть"
        if purpose in ['Просто поиграть', 'Just to play']:
            if country == 'Россия, Белоруссия, Украина':
                found_users = await User.query.where(User.purpose == purpose).where(User.user_id != user_id).where(
                    or_(User.game1 == game1, User.game2 == game2, User.game1 == game2, User.game2 == game1)).where(
                    User.country == 'Россия, Белоруссия, Украина').where(User.enable == True).gino.all()
            else:
                found_users = await User.query.where(User.purpose == purpose).where(User.user_id != user_id).where(
                    or_(User.game1 == game1, User.game2 == game2, User.game1 == game2, User.game2 == game1)).where(
                    User.country.ilike(f'%{country}%')).where(User.enable == True).gino.all()

        # Ищем анкеты, где цель поиска "Человека в реальной жизни"
        else:
            if len(gender) == 2:
                found_users = await User.query.where(User.purpose == purpose).where(User.user_id != user_id).where(
                    User.age > age).where(or_(User.gender == gender[0], User.gender == gender[1])).where(
                    User.country.ilike(f'%{country}%')).where(User.city == city).where(User.enable == True).gino.all()
            else:
                found_users = await User.query.where(User.purpose == purpose).where(User.user_id != user_id).where(
                    User.age > age).where(
                    or_(User.gender == gender[0], User.gender == gender[1], User.gender == gender[2],
                        User.gender == gender[3])).where(User.country.ilike(f'%{country}%')).where(
                    User.city == city).where(User.enable == True).gino.all()

        return found_users


# Функция для создания нового профиля
async def add_new_profile(**kwargs):
    new_profile = await User(**kwargs).create()
    return new_profile
