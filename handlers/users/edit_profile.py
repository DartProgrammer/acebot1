from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from fuzzywuzzy import process

from handlers.users.my_profile import db
from handlers.users.users_info import AgeRestriction, NumberCharacters, InsufficientAge
from keyboards.inline.gaming_keyboards import show_gender_keyboard, show_who_search_keyboard, \
    show_correct_profile_keyboard, show_looking_for_keyboard, get_teammates_country
from loader import dp
from utils import photo_link
from utils.db_api import models


# Узнаем пол пользователя
@dp.message_handler(state='edit_age', content_types=types.ContentTypes.ANY)
async def edit_profile_age(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')

    try:
        age = int(message.text)
        if age > 99:
            raise AgeRestriction
        elif age < 10:
            raise InsufficientAge

    # Если пользователь ввёл текст
    except ValueError:
        if language == '🇷🇺 Русский':
            await message.answer('Введите число')
        else:
            await message.answer('Enter an integer')
        return

    # Если пользователь прислал стикер
    except TypeError:
        if language == '🇷🇺 Русский':
            await message.answer('Введите число')
        else:
            await message.answer('Enter an integer')
        return

    # Если пользователь указал возраст больше 99 лет
    except AgeRestriction:
        if language == '🇷🇺 Русский':
            await message.answer('Укажите правильный возраст')
        else:
            await message.answer('Specify the correct age')
        return

    # Если пользователь указал возраст меньше 10 лет
    except InsufficientAge:
        if language == '🇷🇺 Русский':
            await message.answer('⛔️ВАМ ЗАПРЕЩЕНО ПОЛЬЗОВАТЬСЯ ДАННЫМ БОТОМ⛔️')
        else:
            await message.answer('⛔️YOU ARE NOT ALLOWED TO USE THIS BOT⛔️')
        return

    await state.update_data(age=age)

    # Если пользователю меньше 16 лет
    if age < 16:
        if language == '🇷🇺 Русский':
            await message.answer('Привет, я просто хочу сказать тебе, что в этом мире не все так радужно и беззаботно, '
                                 'полно злых людей, которые выдают себя не за тех, кем являются - никому и никогда не '
                                 'скидывай свои фотографии, никогда не соглашайся на встречи вечером или не в людных '
                                 'местах, и подозревай всех) Я просто переживаю о тебе и береги себя!')
        else:
            await message.answer("Hi, I just want to tell you that in this world, not everything is so rosy and "
                                 "carefree, full of evil people who pretend not to be who they are - never throw off "
                                 "your photos to anyone, never agree to meetings in the evening or not in crowded "
                                 "places, and suspect everyone) I'm just worried about you and take care of yourself!")

    if language == '🇷🇺 Русский':
        await message.answer('Ты парень или девушка?', reply_markup=show_gender_keyboard(language))
    else:
        await message.answer('Are you a guy or a girl?', reply_markup=show_gender_keyboard(language))

    await state.set_state('edit_gender')


# Узнаем цель поиска
@dp.message_handler(state='edit_gender')
async def set_continue(message: types.Message, state: FSMContext):
    gender = message.text
    await state.update_data(gender=gender)
    data = await state.get_data()
    language = data.get('language')
    age = data.get('age')
    text_ru = 'Кого ты ищешь?'
    text_en = 'Who are you looking for?'

    if language == '🇷🇺 Русский':
        await message.answer(text=text_ru, reply_markup=show_looking_for_keyboard(language, age))
    else:
        await message.answer(text=text_en, reply_markup=show_looking_for_keyboard(language, age))

    await state.set_state('edit_looking_for')


# Узнаем, кого ищет пользователь
@dp.message_handler(state='edit_looking_for')
async def edit_profile_gender(message: types.Message, state: FSMContext):
    purpose = message.text
    await state.update_data(purpose=purpose)
    data = await state.get_data()
    language = data.get('language')
    age = data.get('age')

    # Если пользователь выбрал "Просто поиграть"
    if purpose in ['Просто поиграть', 'Just to play']:

        if language == '🇷🇺 Русский':
            await message.answer('Из каких стран вы хотите, что бы были ваши тиммейты?',
                                 reply_markup=get_teammates_country(language))

        else:
            await message.answer('What countries do you want your teammates to be from?',
                                 reply_markup=get_teammates_country(language))

        await state.set_state('edit_profile_just_play')

    # Если пользователь выбрал "Команду для праков"
    elif purpose in ['Команду для праков', 'A team for practitioners']:

        if language == '🇷🇺 Русский':
            await message.answer('Данная функция находится в стадии разработки',
                                 reply_markup=show_looking_for_keyboard(language, age))
        else:
            await message.answer('This feature is under development',
                                 reply_markup=show_looking_for_keyboard(language, age))
        return

    # Если пользователь выбрал "Человека в реальной жизни"
    else:
        if language == '🇷🇺 Русский':
            await message.answer('Кого ты ищешь?', reply_markup=show_who_search_keyboard(language))
        else:
            await message.answer('Who are you looking for?', reply_markup=show_who_search_keyboard(language))

        await state.set_state('edit_who_looking_for')


# Узнаем страну пользователя
@dp.message_handler(state='edit_who_looking_for')
async def edit_profile_who_looking_for(message: types.Message, state: FSMContext):
    who_search = message.text
    await state.update_data(who_search=who_search)
    data = await state.get_data()
    language = data.get('language')
    user: models.User = data.get('user_')

    if language == '🇷🇺 Русский':
        await message.answer('Из какой ты страны?', reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=user.country)
                ]
            ], resize_keyboard=True, one_time_keyboard=True
        ))
    else:
        await message.answer('What country are you from?', reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=user.country)
                ]
            ], resize_keyboard=True, one_time_keyboard=True
        ))

    await state.set_state('edit_country')


# Узнаем город пользователя
@dp.message_handler(state='edit_country')
async def edit_profile_country(message: types.Message, state: FSMContext):
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
        await state.update_data(country=country)

        # Получаем список всех регионов
        all_regions = await db.get_all_regions(country)

        region_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        for region in all_regions:
            region_btn = KeyboardButton(text=f'{region[0]}')
            region_keyboard.add(region_btn)

        if language == '🇷🇺 Русский':
            await message.answer('Из какого ты региона? (выбери из списка)', reply_markup=region_keyboard)
        else:
            await message.answer('What region are you from? (choose from the list)', reply_markup=region_keyboard)

        await state.set_state('edit_region')

    # Если совпадение не 100%
    else:
        if language == '🇷🇺 Русский':
            await message.answer(f'Вы имели ввиду <b>{country_name[0]}</b>?\n'
                                 f'Совпадение: <b>{coincidence}%</b>',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text='✔'),
                                         KeyboardButton(text='❌')
                                     ]
                                 ], resize_keyboard=True, one_time_keyboard=True
                                 ))

        else:
            await message.answer(f'Did you mean <b>{country_name[0]}</b>?\n'
                                 f'Coincidence: <b>{coincidence}%</b>',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [
                                         KeyboardButton(text='✔'),
                                         KeyboardButton(text='❌')
                                     ]
                                 ], resize_keyboard=True, one_time_keyboard=True
                                 ))

        await state.update_data(country=country_name[0])
        await state.set_state('check_edit_country')


# Если пользователь указал страну некорректно, уточняем вариант, найденный в базе
@dp.message_handler(state='check_edit_country')
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

        if language == '🇷🇺 Русский':
            await message.answer('Из какого ты региона? (выбери из списка)', reply_markup=region_keyboard)
        else:
            await message.answer('What region are you from? (choose from the list)', reply_markup=region_keyboard)

        await state.set_state('edit_region')

    # Если пользователь не подтвердил найденную страну
    elif answer == '❌':
        if language == '🇷🇺 Русский':
            await message.answer('Просьба еще раз ввести корректное название страны')
        else:
            await message.answer('Please enter the correct country name again')

        await state.set_state('edit_country')

    # Если пользователь не выбрал вариант, а ввел какой-то текст
    else:
        if language == '🇷🇺 Русский':
            await message.answer('Не знаю такой символ')
        else:
            await message.answer("I don't know such a symbol")


# Узнаем город пользователя
@dp.message_handler(state='edit_region')
async def get_city(message: types.Message, state: FSMContext):
    region = message.text
    await state.update_data(region=region)
    data = await state.get_data()
    language = data.get('language')

    # Получаем список всех городов по выбранному региону
    all_cities = await db.get_all_cities(region)

    cities_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    for city in all_cities:
        city_btn = KeyboardButton(text=f'{city[0]}')
        cities_keyboard.add(city_btn)

    if language == '🇷🇺 Русский':
        await message.answer('Из какого ты города? (выбери из списка)', reply_markup=cities_keyboard)
    else:
        await message.answer('What city are you from? (choose from the list)', reply_markup=cities_keyboard)

    await state.set_state('edit_city')


# Узнаем имя пользователя
@dp.message_handler(state='edit_city')
async def edit_profile_city(message: types.Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)
    data = await state.get_data()
    language = data.get('language')
    user: models.User = data.get('user_')

    if language == '🇷🇺 Русский':
        await message.answer('Как твоё имя?', reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=user.name)
                ]
            ], resize_keyboard=True
        ))
    else:
        await message.answer('What is your name?', reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=user.name)
                ]
            ], resize_keyboard=True
        ))

    await state.set_state('edit_name')


# Узнаем дополнительную информацию о пользователе
@dp.message_handler(state='edit_name')
async def edit_profile_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    data = await state.get_data()
    language = data.get('language')

    if language == '🇷🇺 Русский':
        await message.answer('Расскажи о себе.', reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Пропустить')
                ]
            ], resize_keyboard=True
        ))
    else:
        await message.answer('Tell me about yourself.', reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Skip')
                ]
            ], resize_keyboard=True
        ))

    await state.set_state('edit_about_yourself')


# Узнаем хобби пользователя
@dp.message_handler(state='edit_about_yourself')
async def edit_profile_about_yourself(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = data.get('language')
    about_yourself = message.text
    if about_yourself != 'Пропустить' and about_yourself != 'Skip':
        await state.update_data(about_yourself=about_yourself)
    else:
        await state.update_data(about_yourself=user.about_yourself)

    if language == '🇷🇺 Русский':
        await message.answer('Твои хобби? Напиши через “запятую” то, чем ты любишь заниматься.',
                             reply_markup=ReplyKeyboardMarkup(
                                 keyboard=[
                                     [
                                         KeyboardButton(text='Пропустить')
                                     ]
                                 ], resize_keyboard=True
                             ))
    else:
        await message.answer('Your hobbies? Write with a comma what you like to do.', reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Skip')
                ]
            ], resize_keyboard=True
        ))

    await state.set_state('edit_hobby')


# Просим фотографию пользователя
@dp.message_handler(state='edit_hobby')
async def edit_profile_hobby(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = data.get('language')

    # Проверяем хобби пользователя на количество символов
    try:
        hobby = message.text
        if len(hobby) > 50:
            raise NumberCharacters

    except NumberCharacters:
        hobby = message.text
        if language == '🇷🇺 Русский':
            await message.answer(f'Хобби имеет ограничение по количеству символов = <b>50</b>,\n '
                                 f'ваше хобби имеет количество символов = <b>{len(hobby)}</b>!\n'
                                 f'Укажите хобби покороче.')
            return

        else:
            await message.answer(f'Hobby has a limit on the number of characters = <b>50</b>,\n '
                                 f'your hobby has a number of characters = <b>{len(hobby)}</b>!\n'
                                 f'Specify a shorter hobby.')
            return

    # Если пользователь нажал "Пропустить"
    if hobby != 'Пропустить' and hobby != 'Skip':
        await state.update_data(hobby=hobby)
    else:
        await state.update_data(hobby=user.hobby)

    if language == '🇷🇺 Русский':
        await message.answer('Пришли свое фото (не файл)', reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Оставить текущее')
                ]
            ], resize_keyboard=True
        ))
    else:
        await message.answer('Send your photo (not file)', reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Leave the current')
                ]
            ], resize_keyboard=True
        ))

    await state.set_state('edit_photo')


# Отправляем пользователю его профиль для проверки
@dp.message_handler(state='edit_photo')
async def edit_profile_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    if message.text not in ['Оставить текущее', 'Leave the current', 'Вернуться назад', 'Go back']:
        photo = message.photo[-1]
        link = await photo_link(photo)
        await state.update_data(photo=link)
    else:
        link = user.photo
        await state.update_data(photo=link)

    language = data.get('language')
    age = data.get('age')
    gender = data.get('gender')
    purpose = data.get('purpose')
    who_search = data.get('who_search')
    country = data.get('country')
    city = data.get('city')
    name = data.get('name')
    about_yourself = data.get('about_yourself')
    hobby = data.get('hobby')
    game1 = data.get('game1')
    if game1 is None:
        game1 = user.game1
    game2 = data.get('game2')
    if game2 is None:
        game2 = user.game2

    if game1 is not None and game2 is not None:
        games = f'{game1}, {game2}'
    elif game2 is None:
        games = f'{game1}'
    elif game1 is None:
        games = f'{game2}'
    else:
        games = ''

    text_ru = f'Вот твой профиль:\n\n' \
              f'Имя: <b>{name}</b>\n' \
              f'Возраст: <b>{age}</b>\n' \
              f'Пол: <b>{gender}</b>\n' \
              f'Ищу: <b>{purpose}</b>\n' \
              f'Кого ищу: <b>{who_search}</b>\n' \
              f'Страна: <b>{country}</b>\n' \
              f'Город: <b>{city}</b>\n' \
              f'О себе: <b>{about_yourself}</b>\n' \
              f'Хобби: <b>{hobby}</b>\n' \
              f'В какие игры играю: <b>{games}</b>\n' \
              f'Все верно?'

    text_en = f'Here is your profile:\n\n' \
              f'Name: <b>{name}</b>\n' \
              f'Age: <b>{age}</b>\n' \
              f'Gender: <b>{gender}</b>\n' \
              f'Search: <b>{purpose}</b>\n' \
              f'Who search: <b>{who_search}</b>\n' \
              f'Country: <b>{country}</b>\n' \
              f'City: <b>{city}</b>\n' \
              f'About yourself: <b>{about_yourself}</b>\n' \
              f'Hobby: <b>{hobby}</b>\n' \
              f'Playing games: <b>{games}</b>\n' \
              f'Is that right?'

    if language == '🇷🇺 Русский':
        await message.answer_photo(photo=link, caption=text_ru, reply_markup=show_correct_profile_keyboard(language))
    else:
        await message.answer_photo(photo=link, caption=text_en, reply_markup=show_correct_profile_keyboard(language))

    await state.set_state('edit_check_profile')


# Если пользователь подтвердил изменение профиля
@dp.message_handler(filters.Text(startswith=['Да', 'Yes']), state='edit_check_profile')
async def edit_profile_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = data.get('language')
    age = data.get('age')
    gender = data.get('gender')
    purpose = data.get('purpose')
    who_search = data.get('who_search')
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
        purpose=purpose,
        who_search=who_search,
        country=country,
        city=city,
        about_yourself=about_yourself,
        hobby=hobby,
        photo=str(photo)
    ).apply()

    if language == '🇷🇺 Русский':
        await message.answer('Профиль успешно добавлен! Для перехода в основное меню, нажмите /my_profile',
                             reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer('Profile successfully added! To go to the main menu, press /my_profile',
                             reply_markup=ReplyKeyboardRemove())

    await state.reset_state()
