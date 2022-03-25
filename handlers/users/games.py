from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import ReplyKeyboardRemove

from keyboards.inline.gaming_keyboards import show_games_keyboard
from loader import dp, _


# Сюда попадаем, когда просим пользователя выбрать игры, в которые он играет
@dp.message_handler(state='choice_games')
async def choice_games(message: types.Message, state: FSMContext):
    text = _('Выбери игру (игры), в которые вы играете! После нажатия на одну игру, вы сможете добавить еще одну.')
    await message.answer(text=text, reply_markup=show_games_keyboard())
    await state.set_state('choice_games_more')


# Сюда попадаем, когда пользователь выбрал игру "PUBG MOBILE"
@dp.message_handler(text='PUBG MOBILE', state='choice_games_more')
async def choice_games1(message: types.Message, state: FSMContext):
    game1 = message.text
    data = await state.get_data()
    game2 = data.get('game2')
    await state.update_data(game1=game1)

    if game2 is None:
        text = _('Вы играете в игру <b>{game1}</b>, хотите ли вы добавить еще какую-то игру или будем искать '
                 'людей только в этой игре?').format(game1=game1)
    else:
        text = _('Вы играете в игры <b>{game1}, {game2}</b>, нажмите "Продолжить"').format(game1=game1, game2=game2)

    await message.answer(text=text, reply_markup=show_games_keyboard(game1, game2))


# Сюда попадаем, когда пользователь выбрал игру "PUBG New State"
@dp.message_handler(text='PUBG New State', state='choice_games_more')
async def choice_games2(message: types.Message, state: FSMContext):
    game2 = message.text
    data = await state.get_data()
    game1 = data.get('game1')
    await state.update_data(game2=game2)

    if game1 is None:
        text = _('Вы играете в игру <b>{game2}</b>, хотите ли вы добавить еще какую-то игру или будем искать '
                 'людей только в этой игре?').format(game2=game2)
    else:
        text = _('Вы играете в игры <b>{game1}, {game2}</b>, нажмите "Продолжить"').format(game1=game1, game2=game2)

    await message.answer(text=text, reply_markup=show_games_keyboard(game2, game1))


# Сюда попадаем, когда пользователь нажал "Продолжить". Узнаем возраст пользователя
@dp.message_handler(filters.Text(startswith=['Продолжить', 'Continue'], ignore_case=True), state='choice_games_more')
async def enter_age(message: types.Message, state: FSMContext):
    await message.answer(text=_('Сколько тебе лет?'), reply_markup=ReplyKeyboardRemove())
    await state.set_state('age')
