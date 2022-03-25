from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import show_gender_keyboard, \
    get_level_of_play_keyboard, show_correct_profile_keyboard, menu_my_profile_keyboard
from loader import dp, db, _
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
        await message.answer(_('Ты парень или девушка?'), reply_markup=show_gender_keyboard())
        await state.set_state('gender_just_play_after_change_match')

    # Если пользователь выбрал "Все страны"
    elif countries in ['Все страны', 'All countries']:
        # Получаем список всех стран
        all_countries = await db.get_all_countries()
        country_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for country in all_countries:
            country_btn = KeyboardButton(text=f'{country[0]}')
            country_keyboard.add(country_btn)

        await message.answer(_('Выберите страну из списка'), reply_markup=country_keyboard)
        await state.set_state('country_just_play_after_change_match')

    # Если пользователь не выбрал из вариантов, а написал текст
    else:
        await message.answer(_('Не знаю такой вариант, просьба нажать на одну из кнопок клавиатуры!'))


# Получаем страну, которую пользователь выбрал из списка
@dp.message_handler(state='country_just_play_after_change_match')
async def get_country_just_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')
    country = message.text
    await state.update_data(country=country)
    await message.answer(_('Ты парень или девушка?'), reply_markup=show_gender_keyboard())
    await state.set_state('gender_just_play_after_change_match')


# Узнаем у пользователя его уровень игры
@dp.message_handler(state='gender_just_play_after_change_match')
async def get_level_of_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')

    gender = message.text
    await state.update_data(gender=gender)
    await message.answer(_('Ваш уровень игры?'), reply_markup=get_level_of_play_keyboard())
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
            await message.answer(_('Выберите вариант из списка'))
            return
    except TypeError:
        pass
    await message.answer(_('Ваше К/Д??'))
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
        await message.answer(_('Введите число'))
        return

    await state.update_data(cool_down=cool_down)
    await message.answer(_('Что-то от себя?'))
    await state.set_state('something_from_yourself_after_change_match')


# Запрашиваем у пользователя его фотографию
@dp.message_handler(state='something_from_yourself_after_change_match')
async def get_photo(message: types.Message, state: FSMContext):
    about_yourself = message.text
    await state.update_data(about_yourself=about_yourself)

    await message.answer(_('Пришли любую фотографию (не файл), если хочешь!'),
                         reply_markup=ReplyKeyboardMarkup(keyboard=[
                             [
                                 KeyboardButton(text=_('Пропустить'))
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

    text_ru = _('Вот твой профиль:\n\n'
                'Возраст: <b>{age}</b>\n'
                'Пол: <b>{gender}</b>\n'
                'Цель: <b>{purpose}</b>\n'
                'Страна поиска: <b>{country}</b>\n'
                'О себе: <b>{about_yourself}</b>\n'
                'В какие игры играю: <b>{games}</b>\n'
                'Уровень игры: <b>{play_level}</b>\n'
                'Ваш К/Д: <b>{cool_down}</b>\n\n'
                'Все верно?').format(age=age, gender=gender, purpose=purpose, country=country,
                                     about_yourself=about_yourself, games=games, play_level=play_level,
                                     cool_down=cool_down)

    # Если пользователь не стал отправлять фото, а нажал "Пропустить"
    if message.text in ['Пропустить', 'Skip']:
        await message.answer(text=text_ru, reply_markup=show_correct_profile_keyboard())

    # Если пользователь отправил фото
    else:
        # Проверяем, что пользователь прислал фото, а не файл
        try:
            photo = message.photo[-1]
        except IndexError:
            await message.answer(_('Пришлите фото, не файл!'))
            return

        link = await photo_link(photo)
        await state.update_data(photo=link)
        await message.answer_photo(photo=link, caption=text_ru,
                                   reply_markup=show_correct_profile_keyboard())

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

    text_ru = _('Вот твой профиль:\n\n'
                'Возраст: <b>{age}</b>\n'
                'Пол: <b>{gender}</b>\n'
                'Цель: <b>{purpose}</b>\n'
                'Страна поиска: <b>{country}</b>\n'
                'О себе: <b>{about_yourself}</b>\n'
                'В какие игры играю: <b>{games}</b>\n'
                'Уровень игры: <b>{play_level}</b>\n'
                'Ваш К/Д: <b>{cool_down}</b>').format(age=age, gender=gender, country=country,
                                                      about_yourself=about_yourself, games=games, play_level=play_level,
                                                      cool_down=cool_down)

    await message.answer(_('Профиль успешно добавлен!'))

    if photo == 'None':
        await message.answer(text=text_ru)
    else:
        await message.answer_photo(photo=user.photo, caption=text_ru)

    await message.answer(text=_('1. Заполнить анкету заново\n'
                                '2. Изменить фото\n'
                                '3. Изменить текст анкеты\n'
                                '4. Смотреть анкеты'), reply_markup=menu_my_profile_keyboard)

    await state.set_state('my_profile_state')
