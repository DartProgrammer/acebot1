from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from emoji import emojize
from loader import _

# Клавиатура для выбора языка меню
language_callback = CallbackData('language', 'code')
language_keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)

ru_button = InlineKeyboardButton(text=f'🇷🇺 Русский', callback_data=language_callback.new(code='ru'))
en_button = InlineKeyboardButton(text=f'🇺🇸 English', callback_data=language_callback.new(code='en'))

language_keyboard.add(ru_button, en_button)


# Клавиатура для выбора игр
def show_games_keyboard(game1=None, game2=None):
    games_keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    continue_btn = KeyboardButton(text=_('Продолжить'))

    if game1 is None:
        pubg_mobile_btn = KeyboardButton(text='PUBG MOBILE')
        pubg_new_state_btn = KeyboardButton(text='PUBG New State')
        games_keyboard.add(pubg_mobile_btn, pubg_new_state_btn, continue_btn)

    elif game1 == 'PUBG MOBILE' and game2 is None:
        pubg_new_state_btn = KeyboardButton(text='PUBG New State')
        games_keyboard.add(pubg_new_state_btn, continue_btn)
    elif game1 == 'PUBG New State' and game2 is None:
        pubg_mobile_btn = KeyboardButton(text='PUBG MOBILE')
        games_keyboard.add(pubg_mobile_btn, continue_btn)
    else:
        games_keyboard.add(continue_btn)

    return games_keyboard


# Клавиатура для выбора вариантов, что ищет пользователь
def show_looking_for_keyboard(age):
    looking_for_keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)

    if 9 < age < 12:
        just_play_btn = KeyboardButton(text=_('Просто поиграть'))

        looking_for_keyboard.add(just_play_btn)

    else:
        person_real_life_btn = KeyboardButton(text=_('Человека в реальной жизни'))
        practitioners_team_btn = KeyboardButton(text=_('Команду для праков'))
        just_play_btn = KeyboardButton(text=_('Просто поиграть'))

        looking_for_keyboard.add(person_real_life_btn, just_play_btn, practitioners_team_btn)

    return looking_for_keyboard


# Клавиатура для выбора пола
def show_gender_keyboard():
    gender_keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)

    guy_btn = KeyboardButton(text=_('Парень'))
    girl_btn = KeyboardButton(text=_('Девушка'))

    gender_keyboard.add(guy_btn, girl_btn)

    return gender_keyboard


# Клавиатура для выбора, кого ищет пользователь
def show_who_search_keyboard():
    who_search_keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)

    guys_btn = KeyboardButton(text=_('Парней'))
    girls_btn = KeyboardButton(text=_('Девушек'))
    guys_girls_btn = KeyboardButton(text=_('Парней и Девушек'))

    who_search_keyboard.add(guys_btn, girls_btn, guys_girls_btn)

    return who_search_keyboard


# Клавиатура подтверждения профиля
def show_correct_profile_keyboard():
    correct_profile_keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)

    correct_btn = KeyboardButton(text=_('Да'))
    cancel_btn = KeyboardButton(text=_('Изменить анкету'))

    correct_profile_keyboard.add(correct_btn, cancel_btn)

    return correct_profile_keyboard


# Клавиатура для команды /language
menu_language_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

one_btn = KeyboardButton(text='1')
two_btn = KeyboardButton(text='2')
three_btn = KeyboardButton(text='3')

menu_language_keyboard.add(one_btn, two_btn, three_btn)

# Клавиатура для команды /my_profile
menu_my_profile_keyboard = ReplyKeyboardMarkup(row_width=4, resize_keyboard=True, one_time_keyboard=True)

one_btn = KeyboardButton(text='1')
two_btn = KeyboardButton(text='2')
three_btn = KeyboardButton(text='3')
four_btn = KeyboardButton(text=f'4 {emojize(":magnifying_glass_tilted_right:")}')

menu_my_profile_keyboard.add(one_btn, two_btn, three_btn, four_btn)


# Клавиатура для действий с найденным профилем
def action_for_profile(profiles, count_profiles, current_profile=None):
    profiles_list = profiles
    count_profiles = count_profiles
    if current_profile is not None:
        current_profile = current_profile

    previous_profile = current_profile - 1
    current_profile = current_profile
    next_profile = current_profile + 1

    profile_action_keyboard = ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)

    like_btn = KeyboardButton(text=f'{emojize(":growing_heart:")}')
    love_letter_btn = KeyboardButton(text=f'{emojize(":love_letter:")}')
    dislike_btn = KeyboardButton(text=f'{emojize(":thumbs_down:")}')
    zzz_btn = KeyboardButton(text=f'{emojize(":zzz:")}')

    profile_action_keyboard.add(like_btn, love_letter_btn, dislike_btn, zzz_btn)

    return profile_action_keyboard


# Клавиатура для действий с профилем, которому вы понравились 1
profile_action_like_keyboard = ReplyKeyboardMarkup(row_width=4, resize_keyboard=True, one_time_keyboard=True)

like_target_btn = KeyboardButton(text=f'{emojize(":thumbs_up:")}')
zzz_target_btn = KeyboardButton(text=f'{emojize(":zzz:")}')

profile_action_like_keyboard.add(like_target_btn, zzz_target_btn)

# Клавиатура для действий с профилем, которому вы понравились 2
profile_action_target_keyboard = ReplyKeyboardMarkup(row_width=4, resize_keyboard=True, one_time_keyboard=True)

like_target_btn = KeyboardButton(text=f'{emojize(":growing_heart:")}')
love_letter_target_btn = KeyboardButton(text=f'{emojize(":love_letter:")}')
dislike_target_btn = KeyboardButton(text=f'{emojize(":thumbs_down:")}')
zzz_target_btn = KeyboardButton(text=f'{emojize(":zzz:")}')

profile_action_target_keyboard.add(like_target_btn, love_letter_target_btn, dislike_target_btn, zzz_target_btn)

# Клавиатура при нажатии кнопки "Пожаловаться"
complain_keyboard = ReplyKeyboardMarkup(row_width=5, resize_keyboard=True, one_time_keyboard=True)

adult_btn = KeyboardButton(text=f'{emojize(":no_one_under_eighteen:")} 1')
sale_btn = KeyboardButton(text=f'{emojize(":shopping_cart:")} 2')
not_responding_btn = KeyboardButton(text=f'{emojize(":muted_speaker:")} 3')
other_btn = KeyboardButton(text=f'{emojize(":red_question_mark:")} 4')
cancel_complain_btn = KeyboardButton(text=f'{emojize(":multiply:")} 5')


# Клавиатура для выбора страны teammates
def get_teammates_country():
    teammates_country_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    cis_countries_btn = KeyboardButton(text=_('Страны СНГ'))
    all_countries_btn = KeyboardButton(text=_('Все страны'))

    teammates_country_keyboard.add(cis_countries_btn, all_countries_btn)

    return teammates_country_keyboard


# Клавиатура для выбора уровня игры
def get_level_of_play_keyboard():
    level_of_play_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)

    beginner_btn = KeyboardButton(text=_('Новичок'))
    average_btn = KeyboardButton(text=_('Средний'))
    high_btn = KeyboardButton(text=_('Высокий'))
    cyber_sport_btn = KeyboardButton(text=_('Киберспорт'))

    level_of_play_keyboard.add(beginner_btn, average_btn, high_btn, cyber_sport_btn)

    return level_of_play_keyboard


# Клавиатура для действий при получении письма
def get_send_message_keyboard():
    send_message_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)

    answer_btn = KeyboardButton(text=_('Ответить'))
    complain_btn = KeyboardButton(text=_('⚠️ Пожаловаться'))

    send_message_keyboard.add(answer_btn, complain_btn)

    return send_message_keyboard
