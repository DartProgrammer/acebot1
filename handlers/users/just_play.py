from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import show_gender_keyboard, \
    get_level_of_play_keyboard, show_correct_profile_keyboard, menu_my_profile_keyboard
from loader import dp, db, _
from utils.photo_link import photo_link
from utils.db_api.models import User


# Сюда попадаем, если пользователь выбрал "Просто поиграть"
@dp.message_handler(state='just_play')
async def purpose_search_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')
    countries = message.text

    # Если пользователь выбрал "Страны СНГ"
    if countries in ['Страны СНГ', 'CIS countries']:
        await state.update_data(country='Россия, Белоруссия, Украина')
        await message.answer(_('Ты парень или девушка?'), reply_markup=show_gender_keyboard())
        await state.set_state('gender_just_play')

    # Если пользователь выбрал "Все страны"
    elif countries in ['Все страны', 'All countries']:
        # Получаем список всех стран
        all_countries = await db.get_all_countries()

        country_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        for country in all_countries:
            country_btn = KeyboardButton(text=f'{country[0]}')
            country_keyboard.add(country_btn)

        await message.answer(_('Выберите страну из списка'), reply_markup=country_keyboard)
        await state.set_state('country_just_play')

    # Если пользователь не выбрал из вариантов, а написал текст
    else:
        await message.answer(_('Не знаю такой вариант, просьба нажать на одну из кнопок клавиатуры!'))


# Получаем страну, которую пользователь выбрал из списка
@dp.message_handler(state='country_just_play')
async def get_country_just_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')

    all_countries = await db.get_all_countries()
    country = message.text
    if country not in all_countries:
        await message.answer(_('Не знаю такой вариант, просьба нажать на одну из кнопок клавиатуры!'))
        return

    await state.update_data(country=country)
    await message.answer(_('Ты парень или девушка?'), reply_markup=show_gender_keyboard())
    await state.set_state('gender_just_play')


# Узнаем у пользователя его уровень игры
@dp.message_handler(state='gender_just_play')
async def get_level_of_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')

    gender = message.text
    if gender not in ['Парень', 'Девушка', 'Guy', 'Girl']:
        await message.answer(_('Не знаю такой вариант, просьба нажать на одну из кнопок клавиатуры!'))
        return

    await state.update_data(gender=gender)
    await message.answer(_('Ваш уровень игры?'), reply_markup=get_level_of_play_keyboard())
    await state.set_state('level_of_play')


# Узнаем у пользователя его К/Д
@dp.message_handler(state='level_of_play', content_types=types.ContentTypes.ANY)
async def get_cool_down(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')

    play_level = message.text

    if play_level not in ['Новичок', 'Средний', 'Высокий', 'Киберспорт', 'Beginner', 'Average', 'High', 'Cybersport']:
        await message.answer(_('Не знаю такой вариант, просьба нажать на одну из кнопок клавиатуры!'))
        return

    await state.update_data(play_level=play_level)
    await message.answer(_('Ваше К/Д??'))
    await state.set_state('cool_down')


# Узнаем у пользователя дополнительную информацию
@dp.message_handler(state='cool_down')
async def get_something_from_yourself(message: types.Message, state: FSMContext):
    try:
        cool_down = float(message.text)
    # Если пользователь ввёл текст
    except ValueError:
        await message.answer(_('Введите число'))
        return

    await state.update_data(cool_down=cool_down)
    await message.answer(_('Что-то от себя?'))
    await state.set_state('something_from_yourself')


# Запрашиваем у пользователя его фотографию
@dp.message_handler(state='something_from_yourself')
async def get_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')
    about_yourself = message.text
    await state.update_data(about_yourself=about_yourself)

    await message.answer(_('Пришли любую фотографию (не файл), если хочешь!'),
                         reply_markup=ReplyKeyboardMarkup(keyboard=[
                             [
                                 KeyboardButton(text=_('Пропустить'))
                             ]
                         ], resize_keyboard=True, one_time_keyboard=True))

    await state.set_state('photo_just_play')


# Показываем пользователю его профиль
@dp.message_handler(state='photo_just_play', content_types=types.ContentTypes.ANY)
async def add_profile_just_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')

    age = data.get('age')
    gender = data.get('gender')
    purpose = data.get('purpose')
    country = data.get('country')
    play_level = data.get('play_level')
    cool_down = data.get('cool_down')
    about_yourself = data.get('about_yourself')
    game1 = data.get('game1', '')
    game2 = data.get('game2', '')
    if game1 and game2:
        games = f'{game1}, {game2}'
    else:
        # Мы вошли в ветку, когда одна из игр пустая строка, а может и обе, и прибавив к не пустой строке она
        # не меняется
        games = game1 + game2

    text = _('Вот твой профиль:\n\n'
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
        await message.answer(text=text, reply_markup=show_correct_profile_keyboard())
    # Если пользователь отправил фото
    else:
        # Проверяем, что пользователь прислал фото, а не файл
        try:
            photo = message.photo[-1]
            link = await photo_link(photo)
            await state.update_data(photo=link)
            await message.answer_photo(photo=link, caption=text,
                                       reply_markup=show_correct_profile_keyboard())
            await state.set_state('check_profile_just_play')
        except IndexError:
            await message.answer(_('Пришлите фото, не файл!'))
            return


# Если пользователь подтвердил создание профиля
@dp.message_handler(filters.Text(startswith=['Да', 'Yes'], ignore_case=True), state='check_profile_just_play')
async def correct_profile_just_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    user: User = await db.get_user(user_id)
    language = data.get('language')

    age = data.get('age')
    gender = data.get('gender')
    purpose = data.get('purpose')
    country = data.get('country')
    play_level = data.get('play_level')
    cool_down = data.get('cool_down')
    about_yourself = data.get('about_yourself')
    game1 = data.get('game1', '')
    game2 = data.get('game2', '')
    photo = data.get('photo')
    if game1 and game2:
        games = f'{game1}, {game2}'
    else:
        # Мы вошли в ветку, когда одна из игр пустая строка, а может и обе, и прибавив к не пустой строке она
        # не меняется
        games = game1 + game2

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

    text = _('Вот твой профиль:\n\n'
             'Возраст: <b>{age}</b>\n'
             'Пол: <b>{gender}</b>\n'
             'Цель: <b>{purpose}</b>\n'
             'Страна поиска: <b>{country}</b>\n'
             'О себе: <b>{about_yourself}</b>\n'
             'В какие игры играю: <b>{games}</b>\n'
             'Уровень игры: <b>{play_level}</b>\n'
             'Ваш К/Д: <b>{cool_down}</b>').format(age=age, gender=gender, purpose=purpose, country=country,
                                                   about_yourself=about_yourself, games=games, play_level=play_level,
                                                   cool_down=cool_down)

    await message.answer(_('Профиль успешно добавлен!'))
    await message.answer(_('Ваш профиль:'))
    await message.answer(text=text)
    await message.answer(text=_('1. Заполнить анкету заново\n'
                                '2. Изменить фото\n'
                                '3. Изменить текст анкеты\n'
                                '4. Смотреть анкеты'), reply_markup=menu_my_profile_keyboard)

    await state.set_state('my_profile_state')
