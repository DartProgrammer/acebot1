from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from fuzzywuzzy import process

from data.config import HOBBY_STRING_LENGTH
from handlers.users.start import db
from keyboards.inline.gaming_keyboards import show_gender_keyboard, show_who_search_keyboard, \
    show_correct_profile_keyboard, show_looking_for_keyboard, get_teammates_country
from loader import dp, _
from utils.photo_link import photo_link
from utils.db_api.models import User
from exceptions import *


# Узнаем, кого ищет пользователь
@dp.message_handler(state='age', content_types=types.ContentTypes.ANY)
async def enter_purpose(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')

    try:
        age = int(message.text)
        if age > 99:
            raise AgeRestriction
        elif age < 10:
            raise InsufficientAge

    # Если пользователь ввёл текст
    except (ValueError, TypeError):
        await message.answer(_('Введите число'))
        return
    # Если пользователь указал возраст больше 99 лет
    except AgeRestriction:
        await message.answer(_('Укажите правильный возраст'))
        return

    # Если пользователь указал возраст меньше 10 лет
    except InsufficientAge:
        await message.answer(_('⛔ ️ВАМ ЗАПРЕЩЕНО ПОЛЬЗОВАТЬСЯ ДАННЫМ БОТОМ⛔️ '))
        return

    await state.update_data(age=age)

    # Если пользователю меньше 16 лет
    if age < 16:
        await message.answer(_('Привет, я просто хочу сказать тебе, что в этом мире не все так радужно и беззаботно, '
                               'полно злых людей, которые выдают себя не за тех, кем являются - никому и никогда не '
                               'скидывай свои фотографии, никогда не соглашайся на встречи вечером или не в людных '
                               'местах, и подозревай всех) Я просто переживаю о тебе и береги себя!'))

    await message.answer(text=_('Кого ты ищешь?'), reply_markup=show_looking_for_keyboard(age))
    await state.set_state('looking_for')


# Узнаем пол пользователя
@dp.message_handler(state='looking_for')
async def enter_gender(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')
    age = data.get('age')
    purpose = message.text
    await state.update_data(purpose=purpose)

    # Если пользователь выбрал "Просто поиграть"
    if purpose in ['Просто поиграть', 'Just to play']:
        await message.answer(_('Из каких стран вы хотите, что бы были ваши тиммейты?'),
                             reply_markup=get_teammates_country())
        await state.set_state('just_play')
    # Если пользователь выбрал "Команду для праков"
    elif purpose in ['Команду для праков', 'A team for practitioners']:
        await message.answer(_('Данная функция находится в стадии разработки'),
                             reply_markup=show_looking_for_keyboard(age))
        return
    # Если пользователь выбрал "Человека в реальной жизни"
    elif purpose in ['Человека в реальной жизни', 'A person in real life']:
        await message.answer(_('Ты парень или девушка?'), reply_markup=show_gender_keyboard())
        await state.set_state('gender')
    else:
        await message.answer(_('Не знаю такой вариант, просьба нажать на одну из кнопок клавиатуры!'))


# Узнаем, кого ищет пользователь
@dp.message_handler(state='gender')
async def get_who_search(message: types.Message, state: FSMContext):
    gender = message.text
    await state.update_data(gender=gender)
    data = await state.get_data()
    language = data.get('language')

    if gender not in ['Парень', 'Девушка', 'Guy', 'Girl']:
        await message.answer(_('Не знаю такой вариант, просьба нажать на одну из кнопок клавиатуры!'))
        return

    await message.answer(_('Кого ты ищешь?'), reply_markup=show_who_search_keyboard())
    await state.set_state('who_looking_for')


# Узнаем страну пользователя
@dp.message_handler(state='who_looking_for')
async def get_country(message: types.Message, state: FSMContext):
    who_search = message.text
    await state.update_data(who_search=who_search)

    if who_search not in ['Парней', 'Девушек', 'Парней и Девушек', 'Guys', 'Girls', 'Guys and Girls']:
        await message.answer(_('Не знаю такой вариант, просьба нажать на одну из кнопок клавиатуры!'))
        return

    await message.answer(_('Из какой ты страны?'), reply_markup=ReplyKeyboardRemove())
    await state.set_state('country')


# Узнаем город пользователя
@dp.message_handler(state='country')
async def get_region(message: types.Message, state: FSMContext):
    country = message.text
    data = await state.get_data()
    language = data.get('language')

    # Получаем список всех стран
    all_countries = await db.get_all_countries()

    # Ищем совпадение страны, которую написал пользователь, со странами из БД
    country_db = process.extractOne(country, all_countries)
    country_name, coincidence = country_db

    # Если совпадение 100%
    if coincidence == 100:
        country = country_name[0]
        await state.update_data(country=country_name[0])

        # Получаем список всех регионов
        all_regions = await db.get_all_regions(country)

        region_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        for region in all_regions:
            region_btn = KeyboardButton(text=f'{region[0]}')
            region_keyboard.add(region_btn)

        await message.answer(_('Из какого ты региона? (выбери из списка)'), reply_markup=region_keyboard)
        await state.set_state('region')

    # Если совпадение не 100%
    else:
        await message.answer(_('Вы имели ввиду <b>{country_name}</b>?\n'
                               'Совпадение: <b>{coincidence}%</b>').format(country_name=country_name[0],
                                                                           coincidence=coincidence),
                             reply_markup=ReplyKeyboardMarkup(keyboard=[
                                 [
                                     KeyboardButton(text='✔'),
                                     KeyboardButton(text='❌')
                                 ]
                             ], resize_keyboard=True, one_time_keyboard=True
                             ))

        await state.update_data(country=country_name[0])
        await state.set_state('check_country')


# Если пользователь указал страну некорректно, уточняем вариант, найденный в базе
@dp.message_handler(state='check_country')
async def check_country(message: types.Message, state: FSMContext):
    answer = message.text
    data = await state.get_data()
    language = data.get('language')
    country = data.get('country')

    # Если пользователь подтвердил найденную страну
    if answer == '✔':
        await state.update_data(country=country)

        # Получаем список всех регионов
        all_regions = await db.get_all_regions(country)

        region_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        for region in all_regions:
            region_btn = KeyboardButton(text=f'{region[0]}')
            region_keyboard.add(region_btn)

        await message.answer(_('Из какого ты региона? (выбери из списка)'), reply_markup=region_keyboard)
        await state.set_state('region')

    # Если пользователь не подтвердил найденную страну
    elif answer == '❌':
        await message.answer(_('Просьба еще раз ввести корректное название страны'))
        await state.set_state('country')

    # Если пользователь не выбрал вариант, а ввел какой-то текст
    else:
        await message.answer(_('Не знаю такой символ'))


# Узнаем город пользователя
@dp.message_handler(state='region')
async def get_city(message: types.Message, state: FSMContext):
    region = message.text
    await state.update_data(region=region)
    data = await state.get_data()
    language = data.get('language')
    country = data.get('country')

    all_regions = await db.get_all_regions(country)
    all_regions = [item[0] for item in all_regions]
    if region not in all_regions:
        await message.answer(_('Не знаю такой вариант, просьба нажать на одну из кнопок клавиатуры!'))
        return

    # Получаем список всех городов по выбранному региону
    all_cities = await db.get_all_cities(region)
    cities_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    for city in all_cities:
        city_btn = KeyboardButton(text=f'{city[0]}')
        cities_keyboard.add(city_btn)

    await message.answer(_('Из какого ты города? (выбери из списка)'), reply_markup=cities_keyboard)
    await state.set_state('city')


# Узнаем имя пользователя
@dp.message_handler(state='city')
async def get_name(message: types.Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)
    data = await state.get_data()

    all_cities = await db.get_all_cities(data.get('region'))
    all_cities = [item[0] for item in all_cities]
    if city not in all_cities:
        await message.answer(_('Не знаю такой вариант, просьба нажать на одну из кнопок клавиатуры!'))
        return

    await message.answer(_('Как твоё имя?'), reply_markup=ReplyKeyboardRemove())
    await state.set_state('name')

    # # Получаем список всех городов
    # all_cities = await db.get_all_cities()
    #
    # # Ищем совпадение города, который написал пользователь, с городами из БД
    # city_db = process.extract(city, all_cities)
    #
    # city_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    #
    # for city_name, coincidence in city_db:
    #     if coincidence > 90:
    #         city_btn = KeyboardButton(text=f'{city_name[0]}')
    #         city_keyboard.add(city_btn)
    #
    # await message.answer('Выберите правильный вариант', reply_markup=city_keyboard)
    #
    # await state.set_state('check_city')


# Получаем название города, выбранный пользователем
# @dp.message_handler(state='check_city')
# async def get_name(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     language = data.get('language')
#     city = message.text
#
#     await state.update_data(city=city)
#
#     if language == '🇷🇺 Русский':
#         await message.answer('Как твоё имя?')
#     else:
#         await message.answer('What is your name?')
#
#     await state.set_state('name')


# Узнаем дополнительную информацию о пользователе
@dp.message_handler(state='name')
async def get_about_yourself(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(_('Расскажи о себе.'))
    await state.set_state('about_yourself')


# Узнаем хобби пользователя
@dp.message_handler(state='about_yourself')
async def get_hobby(message: types.Message, state: FSMContext):
    await state.update_data(about_yourself=message.text)
    await message.answer(_('Твои хобби? Напиши через “запятую” то, чем ты любишь заниматься.'))
    await state.set_state('hobby')


# Просим фотографию пользователя
@dp.message_handler(state='hobby')
async def get_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')

    # Проверяем хобби пользователя на количество символов
    try:
        hobby = message.text
        if len(hobby) > HOBBY_STRING_LENGTH:
            raise NumberCharacters

    except NumberCharacters:
        hobby = message.text
        await message.answer(_('Хобби имеет ограничение по количеству символов = <b>{HOBBY_STRING_LENGTH}</b>,\n '
                               'ваше хобби имеет количество символов = <b>{length}</b>!\n'
                               'Укажите хобби покороче.').format(HOBBY_STRING_LENGTH=HOBBY_STRING_LENGTH,
                                                                 length=len(hobby)))
        return

    await state.update_data(hobby=hobby)
    await message.answer(_('Пришли свое фото (не файл)'))
    await state.set_state('photo')


# Отправляем пользователю его профиль для проверки
@dp.message_handler(state='photo', content_types=types.ContentTypes.ANY)
async def add_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')

    # Проверяем, что пользователь прислал фото, а не файл
    try:
        photo = message.photo[-1]
    except IndexError:
        await message.answer(_('Пришлите фото, не файл!'))
        return

    link = await photo_link(photo)
    await state.update_data(photo=link)

    age = data.get('age')
    gender = data.get('gender')
    who_search = data.get('who_search')
    purpose = data.get('purpose')
    country = data.get('country')
    city = data.get('city')
    name = data.get('name')
    about_yourself = data.get('about_yourself')
    hobby = data.get('hobby')
    game1 = data.get('game1', '')
    game2 = data.get('game2', '')
    if game1 and game2:
        games = f'{game1}, {game2}'
    else:
        # Мы вошли в ветку, когда одна из игр пустая строка, а может и обе, и прибавив к не пустой строке она
        # не меняется
        games = game1 + game2

    text = _('Вот твой профиль:\n\n'
             'Имя: <b>{name}</b>\n'
             'Возраст: <b>{age}</b>\n'
             'Пол: <b>{gender}</b>\n'
             'Ищу: <b>{purpose}</b>\n'
             'Кого ищу: <b>{who_search}</b>\n'
             'Страна: <b>{country}</b>\n'
             'Город: <b>{city}</b>\n'
             'О себе: <b>{about_yourself}</b>\n'
             'Хобби: <b>{hobby}</b>\n'
             'В какие игры играю: <b>{games}</b>\n'
             'Все верно?').format(name=name, age=age, gender=gender, purpose=purpose, who_search=who_search,
                                  country=country, city=city, about_yourself=about_yourself, hobby=hobby, games=games)

    await message.answer_photo(photo=link, caption=text, reply_markup=show_correct_profile_keyboard())
    await state.set_state('check_profile')


# Если пользователь подтвердил создание профиля
@dp.message_handler(filters.Text(startswith=['Да', 'Yes'], ignore_case=True), state='check_profile')
async def correct_profile(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    user: User = await db.get_user(user_id)
    language = data.get('language')
    age = data.get('age')
    gender = data.get('gender')
    who_search = data.get('who_search')
    purpose = data.get('purpose')
    country = data.get('country')
    city = data.get('city')
    name = data.get('name')
    about_yourself = data.get('about_yourself')
    hobby = data.get('hobby')
    game1 = data.get('game1')
    game2 = data.get('game2')
    photo = data.get('photo')

    await user.update(
        name=name,
        game1=game1,
        game2=game2,
        age=age,
        gender=gender,
        who_search=who_search,
        purpose=purpose,
        country=country,
        city=city,
        about_yourself=about_yourself,
        hobby=hobby,
        photo=str(photo)
    ).apply()

    await message.answer(_('Профиль успешно добавлен! Для перехода в основное меню, нажмите /my_profile'),
                         reply_markup=ReplyKeyboardRemove())
    await state.reset_state()
