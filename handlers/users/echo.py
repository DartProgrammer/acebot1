from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    await message.answer(
        "Вы зачем бота ломаете -_-. Не ломайте его пожалуйста, а если что-то сработало "
        "некорректно, то отправьте пожалуйста скрин @boost_ace")


# Эхо хендлер, куда летят ВСЕ сообщения с указанным состоянием
@dp.message_handler(state="*", content_types=types.ContentTypes.ANY)
async def bot_echo_all(message: types.Message, state: FSMContext):
    await message.answer("Вы зачем бота ломаете -_-. Не ломайте его пожалуйста, а "
                         "если что-то сработало некорректно, то отправьте пожалуйста скрин @boost_ace")
