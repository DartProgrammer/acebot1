from typing import Tuple, Any, Optional

from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware


async def get_user_locale(user_id: int):
    from loader import db
    user = await db.get_user(user_id)
    return user


class LanguageMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        user = types.User.get_current()
        return await get_user_locale(user.id) or user.locale
