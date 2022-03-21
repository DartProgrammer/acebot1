# Класс для отлавливания ограничений по возрасту
class AgeRestriction(BaseException):
    pass


# Класс для пользователей меньше 10 лет
class InsufficientAge(BaseException):
    pass


# Класс для отлавливания ограничений по количеству символов
class NumberCharacters(BaseException):
    pass
