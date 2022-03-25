from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.inline.gaming_keyboards import get_level_of_play_keyboard, show_correct_profile_keyboard, \
    menu_my_profile_keyboard
from keyboards.inline.gaming_keyboards import ru_button
from loader import dp, _
from utils.photo_link import photo_link
from utils.db_api import models
from utils.db_api.models import User


# Сюда попадаем, если пользователь выбрал "Просто поиграть"
@dp.message_handler(state='edit_profile_just_play')
async def purpose_search_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')
    countries = message.text

    # Если пользователь выбрал "Страны СНГ"
    if countries in ['Страны СНГ', 'CIS countries']:
        await state.update_data(country='Россия, Белоруссия, Украина')
    # Если пользователь выбрал "Все страны"
    else:
        await state.update_data(country='Все страны')

    await message.answer(_('Ваш уровень игры?'), reply_markup=get_level_of_play_keyboard())
    await state.set_state('edit_profile_just_play_level_of_play')


# Узнаем у пользователя его К/Д
@dp.message_handler(state='edit_profile_just_play_level_of_play', content_types=types.ContentTypes.ANY)
async def get_cool_down(message: types.Message, state: FSMContext):
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
    await state.set_state('edit_profile_cool_down')


# Узнаем у пользователя дополнительную информацию
@dp.message_handler(state='edit_profile_cool_down')
async def get_something_from_yourself(message: types.Message, state: FSMContext):
    try:
        cool_down = int(message.text)
    # Если пользователь ввёл текст
    except ValueError:
        await message.answer(_('Введите число'))
        return

    await state.update_data(cool_down=cool_down)

    await message.answer(_('Что-то от себя?'))
    await state.set_state('edit_profile_something_from_yourself')


# Запрашиваем у пользователя его фотографию
@dp.message_handler(state='edit_profile_something_from_yourself')
async def get_photo(message: types.Message, state: FSMContext):
    about_yourself = message.text
    await state.update_data(about_yourself=about_yourself)

    await message.answer(_('Пришли свое фото (не файл)'),
                         reply_markup=ReplyKeyboardMarkup(keyboard=[
                             [
                                 KeyboardButton(text=_('Пропустить'))
                             ]
                         ], resize_keyboard=True, one_time_keyboard=True))

    await state.set_state('edit_profile_photo_just_play')


# Показываем пользователю его профиль
@dp.message_handler(state='edit_profile_photo_just_play', content_types=types.ContentTypes.ANY)
async def add_profile_just_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')
    user: models.User = data.get('user_')

    age = data.get('age')
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
        except IndexError:
            if language == ru_button.text:
                await message.answer('Пришлите фото, не файл!')
                return
            else:
                await message.answer('Send a photo, not a file!')
                return

        link = await photo_link(photo)
        await state.update_data(photo=link)

        await message.answer_photo(photo=link, caption=text,
                                   reply_markup=show_correct_profile_keyboard())

    await state.set_state('edit_profile_check_profile_just_play')


# Если пользователь подтвердил создание профиля
@dp.message_handler(filters.Text(startswith=['Да', 'Yes']), state='edit_profile_check_profile_just_play')
async def correct_profile_just_play(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user: User = data.get('user_')
    language = data.get('language')

    age = data.get('age')
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
    await message.answer(text=text)
    await message.answer(text=_('1. Заполнить анкету заново\n'
                                '2. Изменить фото\n'
                                '3. Изменить текст анкеты\n'
                                '4. Смотреть анкеты'), reply_markup=menu_my_profile_keyboard)

    await state.set_state('my_profile_state')
