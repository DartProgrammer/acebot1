from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import show_gender_keyboard, \
    get_level_of_play_keyboard, show_correct_profile_keyboard, menu_my_profile_keyboard
from keyboards.inline.gaming_keyboards import ru_button
from loader import dp, db
from utils.photo_link import photo_link
from utils.db_api import models


# Сюда попадаем, если пользователь изменил цель поиска на "Просто поиграть"
@dp.message_handler(state='just_play_after_change_match')
async def purpose_search_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')
    countries = message.text

    # Если пользователь выбрал "Страны СНГ"
    if countries in ['Страны СНГ', 'CIS countries']:
        await state.update_data(country='Россия, Белоруссия, Украина')

        if language == ru_button.text:
            await message.answer('Ты парень или девушка?', reply_markup=show_gender_keyboard(language))
        else:
            await message.answer('Are you a guy or a girl?', reply_markup=show_gender_keyboard(language))

        await state.set_state('gender_just_play_after_change_match')

    # Если пользователь выбрал "Все страны"
    elif countries in ['Все страны', 'All countries']:

        # Получаем список всех стран
        all_countries = await db.get_all_countries()

        country_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        for country in all_countries:
            country_btn = KeyboardButton(text=f'{country[0]}')
            country_keyboard.add(country_btn)

        if language == ru_button.text:
            await message.answer('Выберите страну из списка', reply_markup=country_keyboard)
        else:
            await message.answer('Choose a country from the list', reply_markup=country_keyboard)

        await state.set_state('country_just_play_after_change_match')

    # Если пользователь не выбрал из вариантов, а написал текст
    else:
        if language == ru_button.text:
            await message.answer('Не знаю такой вариант, просьба нажать на одну из кнопок клавиатуры!')
        else:
            await message.answer('I do not know such an option, please click on one of the keyboard buttons!')


# Получаем страну, которую пользователь выбрал из списка
@dp.message_handler(state='country_just_play_after_change_match')
async def get_country_just_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')

    country = message.text
    await state.update_data(country=country)

    if language == ru_button.text:
        await message.answer('Ты парень или девушка?', reply_markup=show_gender_keyboard(language))
    else:
        await message.answer('Are you a guy or a girl?', reply_markup=show_gender_keyboard(language))

    await state.set_state('gender_just_play_after_change_match')


# Узнаем у пользователя его уровень игры
@dp.message_handler(state='gender_just_play_after_change_match')
async def get_level_of_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')

    gender = message.text
    await state.update_data(gender=gender)

    if language == ru_button.text:
        await message.answer('Ваш уровень игры?', reply_markup=get_level_of_play_keyboard(language))
    else:
        await message.answer('Your level of play?', reply_markup=get_level_of_play_keyboard(language))

    await state.set_state('level_of_play_after_change_match')


# Узнаем у пользователя его К/Д
@dp.message_handler(state='level_of_play_after_change_match', content_types=types.ContentTypes.ANY)
async def get_cool_down(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')

    play_level = message.text

    try:
        if play_level in ['Новичок', 'Средний', 'Высокий', 'Киберспорт', 'Beginner', 'Average', 'High', 'Cybersport']:
            await state.update_data(play_level=play_level)

        else:
            if language == ru_button.text:
                await message.answer('Выберите вариант из списка')
            else:
                await message.answer('Choose an option from the list')
            return

    except TypeError:
        pass

    if language == ru_button.text:
        await message.answer('Ваше К/Д??')
    else:
        await message.answer('Your cool down?')

    await state.set_state('cool_down_after_change_match')


# Узнаем у пользователя дополнительную информацию
@dp.message_handler(state='cool_down_after_change_match')
async def get_something_from_yourself(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')

    try:
        cool_down = float(message.text)

    # Если пользователь ввёл текст
    except ValueError:
        if language == ru_button.text:
            await message.answer('Введите число')
        else:
            await message.answer('Enter an integer')
        return

    await state.update_data(cool_down=cool_down)

    if language == ru_button.text:
        await message.answer('Что-то от себя?')
    else:
        await message.answer('Something from yourself?')

    await state.set_state('something_from_yourself_after_change_match')


# Запрашиваем у пользователя его фотографию
@dp.message_handler(state='something_from_yourself_after_change_match')
async def get_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')
    about_yourself = message.text
    await state.update_data(about_yourself=about_yourself)

    if language == ru_button.text:
        await message.answer('Пришли любую фотографию (не файл), если хочешь!',
                             reply_markup=ReplyKeyboardMarkup(keyboard=[
                                 [
                                     KeyboardButton(text='Пропустить')
                                 ]
                             ], resize_keyboard=True, one_time_keyboard=True))
    else:
        await message.answer('Send any photo (not file) if you want!',
                             reply_markup=ReplyKeyboardMarkup(keyboard=[
                                 [
                                     KeyboardButton(text='Skip')
                                 ]
                             ], resize_keyboard=True, one_time_keyboard=True))

    await state.set_state('photo_just_play_after_change_match')


# Показываем пользователю его профиль
@dp.message_handler(state='photo_just_play_after_change_match', content_types=types.ContentTypes.ANY)
async def add_profile_just_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = data.get('language')

    age = user.age
    gender = data.get('gender')
    purpose = data.get('purpose')
    country = data.get('country')
    play_level = data.get('play_level')
    cool_down = data.get('cool_down')
    about_yourself = data.get('about_yourself')
    game1 = user.game1
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
              f'Возраст: <b>{age}</b>\n' \
              f'Пол: <b>{gender}</b>\n' \
              f'Цель: <b>{purpose}</b>\n' \
              f'Страна поиска: <b>{country}</b>\n' \
              f'О себе: <b>{about_yourself}</b>\n' \
              f'В какие игры играю: <b>{games}</b>\n' \
              f'Уровень игры: <b>{play_level}</b>\n' \
              f'Ваш К/Д: <b>{cool_down}</b>\n\n' \
              f'Все верно?'

    text_en = f'Here is your profile:\n\n' \
              f'Age: <b>{age}</b>\n' \
              f'Gender: <b>{gender}</b>\n' \
              f'Purpose: <b>{purpose}</b>\n' \
              f'Country teammates: <b>{country}</b>\n' \
              f'About yourself: <b>{about_yourself}</b>\n' \
              f'Playing games: <b>{games}</b>\n' \
              f'Level of play: <b>{play_level}</b>\n' \
              f'Your cool down: <b>{cool_down}</b>\n\n' \
              f'Is that right?'

    # Если пользователь не стал отправлять фото, а нажал "Пропустить"
    if message.text in ['Пропустить', 'Skip']:
        if language == ru_button.text:
            await message.answer(text=text_ru, reply_markup=show_correct_profile_keyboard(language))
        else:
            await message.answer(text=text_ru, reply_markup=show_correct_profile_keyboard(language))

    # Если пользователь отправил фото
    else:
        # Проверяем, что пользователь прислал фото, а не файл
        try:
            photo = message.photo[-1]

        except IndexError:
            if language == ru_button.text:
                await message.answer('Пришлите фото, не файл!')
                return
            else:
                await message.answer('Send a photo, not a file!')
                return

        link = await photo_link(photo)
        await state.update_data(photo=link)

        if language == ru_button.text:
            await message.answer_photo(photo=link, caption=text_ru,
                                       reply_markup=show_correct_profile_keyboard(language))
        else:
            await message.answer_photo(photo=link, caption=text_en,
                                       reply_markup=show_correct_profile_keyboard(language))

    await state.set_state('check_profile_just_play_after_change_match')


# Если пользователь подтвердил создание профиля
@dp.message_handler(filters.Text(startswith=['Да', 'Yes'], ignore_case=True),
                    state='check_profile_just_play_after_change_match')
async def correct_profile_just_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: models.User = data.get('user_')
    language = data.get('language')

    age = user.age
    gender = data.get('gender')
    purpose = data.get('purpose')
    country = data.get('country')
    play_level = data.get('play_level')
    cool_down = data.get('cool_down')
    about_yourself = data.get('about_yourself')
    game1 = user.game1
    game2 = user.game2
    photo = data.get('photo')

    if game1 is not None and game2 is not None:
        games = f'{game1}, {game2}'
    elif game2 is None:
        games = f'{game1}'
    elif game1 is None:
        games = f'{game2}'
    else:
        games = ''

    await user.update(
        game1=game1,
        game2=game2,
        age=age,
        gender=gender,
        purpose=purpose,
        country=country,
        play_level=play_level,
        cool_down=cool_down,
        about_yourself=about_yourself,
        photo=str(photo)
    ).apply()

    text_ru = f'Вот твой профиль:\n\n' \
              f'Возраст: <b>{age}</b>\n' \
              f'Пол: <b>{gender}</b>\n' \
              f'Цель: <b>{purpose}</b>\n' \
              f'Страна поиска: <b>{country}</b>\n' \
              f'О себе: <b>{about_yourself}</b>\n' \
              f'В какие игры играю: <b>{games}</b>\n' \
              f'Уровень игры: <b>{play_level}</b>\n' \
              f'Ваш К/Д: <b>{cool_down}</b>'

    text_en = f'Here is your profile:\n\n' \
              f'Age: <b>{age}</b>\n' \
              f'Gender: <b>{gender}</b>\n' \
              f'Purpose: <b>{purpose}</b>\n' \
              f'Country teammates: <b>{country}</b>\n' \
              f'About yourself: <b>{about_yourself}</b>\n' \
              f'Playing games: <b>{games}</b>\n' \
              f'Level of play: <b>{play_level}</b>\n' \
              f'Your cool down: <b>{cool_down}</b>'

    if language == ru_button.text:
        await message.answer('Профиль успешно добавлен!')

        if photo == 'None':
            await message.answer(text=text_ru)
        else:
            await message.answer_photo(photo=user.photo, caption=text_ru)

        await message.answer(text='1. Заполнить анкету заново\n'
                                  '2. Изменить фото\n'
                                  '3. Изменить текст анкеты\n'
                                  '4. Смотреть анкеты', reply_markup=menu_my_profile_keyboard)
    else:
        await message.answer('Profile successfully added!')

        if photo == 'None':
            await message.answer(text=text_en)
        else:
            await message.answer_photo(photo=user.photo, caption=text_en)

        await message.answer(text='1. Edit my profile\n'
                                  '2. Change my photo\n'
                                  '3. Change profile text\n'
                                  '4. View profiles', reply_markup=menu_my_profile_keyboard)

    await state.set_state('my_profile_state')
