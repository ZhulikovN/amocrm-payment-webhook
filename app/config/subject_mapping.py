"""Справочник маппинга предметов из amoCRM в subject_designation платформы."""

from app.settings import settings


def get_subject_mapping() -> dict[int, str]:
    """
    Возвращает маппинг ID предметов из amoCRM в subject_designation платформы.

    Ключ: enum_id из поля 'Какой предмет выбрал' в amoCRM
    Значение: subject_designation для платформы

    Returns:
        dict[int, str]: Словарь маппинга предметов
    """
    return {
        settings.AMO_SUBJECT_OBSHCHESTVO: "social",  # Обществознание → social
        settings.AMO_SUBJECT_ENGLISH: "english",  # Английский язык → english
        settings.AMO_SUBJECT_HISTORY: "history",  # История → history
        settings.AMO_SUBJECT_RUSSIAN: "russian",  # Русский → russian
        settings.AMO_SUBJECT_PHYSICS: "physics",  # Физика → physics
        settings.AMO_SUBJECT_CHEMISTRY: "chemistry",  # Химия → chemistry
        settings.AMO_SUBJECT_LITERATURE: "literature",  # Литература → literature
        settings.AMO_SUBJECT_MATH_PROF_MASHA: "maths",  # Проф. мат (Маша) → maths
        settings.AMO_SUBJECT_MATH_BASE: "maths-base",  # Математика (база) → maths-base
        settings.AMO_SUBJECT_BIOLOGY_ZHENYA: "biology",  # Биология (Женя) → biology
        settings.AMO_SUBJECT_INFORMATICS: "informatics",  # Информатика → informatics
        settings.AMO_SUBJECT_MATH_PROF_SASHA: "maths2",  # Проф. мат (Саша) → maths2
        settings.AMO_SUBJECT_BIOLOGY_GELYA: "biology2",  # Биология (Геля) → biology2
        settings.AMO_SUBJECT_MATH_7_8: "middle_math",  # Математика 7-8 класс → middle_math
        settings.AMO_SUBJECT_MATH_OGE: "maths-oge",  # Математика ОГЭ → maths-oge
    }


def get_subject_name_by_id(subject_id: int) -> str:
    """
    Возвращает название предмета по его ID из amoCRM.

    Args:
        subject_id: ID предмета из amoCRM

    Returns:
        str: Название предмета для логирования

    Raises:
        ValueError: Если предмет с таким ID не найден
    """
    subject_names = {
        settings.AMO_SUBJECT_OBSHCHESTVO: "Обществознание",
        settings.AMO_SUBJECT_ENGLISH: "Английский язык",
        settings.AMO_SUBJECT_HISTORY: "История",
        settings.AMO_SUBJECT_RUSSIAN: "Русский",
        settings.AMO_SUBJECT_PHYSICS: "Физика",
        settings.AMO_SUBJECT_CHEMISTRY: "Химия",
        settings.AMO_SUBJECT_LITERATURE: "Литература",
        settings.AMO_SUBJECT_MATH_PROF_MASHA: "Профиль Маша",
        settings.AMO_SUBJECT_MATH_BASE: "База матем",
        settings.AMO_SUBJECT_BIOLOGY_ZHENYA: "Биология Женя",
        settings.AMO_SUBJECT_INFORMATICS: "Информатика",
        settings.AMO_SUBJECT_MATH_PROF_SASHA: "Профиль Саша",
        settings.AMO_SUBJECT_BIOLOGY_GELYA: "Биология Геля",
        settings.AMO_SUBJECT_MATH_7_8: "Математика 7-8 класс",
        settings.AMO_SUBJECT_MATH_OGE: "Математика ОГЭ",
    }

    if subject_id not in subject_names:
        raise ValueError(f"Неизвестный ID предмета: {subject_id}")

    return subject_names[subject_id]


def map_subject_to_designation(subject_id: int) -> str:
    """
    Преобразует ID предмета из amoCRM в subject_designation для платформы.

    Args:
        subject_id: ID предмета из поля 'Какой предмет выбрал' в amoCRM

    Returns:
        str: subject_designation для платформы

    Raises:
        ValueError: Если маппинг для предмета не найден
    """
    mapping = get_subject_mapping()

    if subject_id not in mapping:
        try:
            subject_name = get_subject_name_by_id(subject_id)
            raise ValueError(f"Маппинг для предмета '{subject_name}' (ID: {subject_id}) не найден")
        except ValueError as exc:
            raise ValueError(f"Маппинг для предмета с ID {subject_id} не найден") from exc

    return mapping[subject_id]


def get_class_mapping() -> dict[int, int]:
    """
    Возвращает маппинг ID классов из amoCRM в числовое значение класса.

    Ключ: enum_id из поля 'В каком классе учится' в amoCRM
    Значение: числовой номер класса для платформы

    Returns:
        dict[int, int]: Словарь маппинга классов
    """
    return {
        settings.AMO_CLASS_5_6: 6,  # 5-6 класс → 6
        settings.AMO_CLASS_7: 7,  # 7 класс → 7
        settings.AMO_CLASS_8: 8,  # 8 класс → 8
        settings.AMO_CLASS_9: 9,  # 9 класс → 9
        settings.AMO_CLASS_10: 10,  # 10 класс → 10
        settings.AMO_CLASS_11: 11,  # 11 класс → 11
        settings.AMO_CLASS_YOUNGER_9: 8,  # Младше 9 класса → 8 (по умолчанию)
        settings.AMO_CLASS_UNIVERSITY: 11,  # Университет → 11
        settings.AMO_CLASS_NOT_STUDENT: 11,  # Не ученик → 11
    }


def map_class_to_number(class_id: int | str) -> int:
    """
    Преобразует ID класса из amoCRM в числовое значение для платформы.
    
    Поддерживает два формата:
    1. Старый формат: enum_id (1374875) → маппинг в число
    2. Новый формат: текст ("11") → прямое преобразование в число

    Args:
        class_id: ID класса (enum_id) или текст ("7", "8", "9", "10", "11")

    Returns:
        int: Номер класса (1-11) для платформы

    Raises:
        ValueError: Если маппинг для класса не найден
    """
    # Если пришла строка - пробуем преобразовать напрямую
    if isinstance(class_id, str):
        try:
            class_number = int(class_id)
            if 1 <= class_number <= 11:
                return class_number
            raise ValueError(f"Класс {class_number} вне диапазона 1-11")
        except ValueError:
            raise ValueError(f"Невозможно преобразовать класс '{class_id}' в число")
    
    # Если пришло число - проверяем маппинг (старый формат с enum_id)
    mapping = get_class_mapping()

    if class_id not in mapping:
        raise ValueError(f"Маппинг для класса с ID {class_id} не найден")

    return mapping[class_id]


def get_tariff_suffix_mapping() -> dict[int, str]:
    """
    Возвращает маппинг ID тарифов в суффикс для названия курса.

    Ключ: enum_id из поля 'Какой курс куплен' в amoCRM
    Значение: суффикс для добавления к названию курса

    Returns:
        dict[int, str]: Словарь маппинга тарифов
    """
    return {
        settings.AMO_COURSE_STANDART: "Standart",
        settings.AMO_COURSE_SAMOSTOYATELNYY: "Самостоятельный",
        settings.AMO_COURSE_PRO: "PRO",
    }


def get_tariff_suffix(tariff_id: int | None) -> str:
    """
    Получить суффикс тарифа для названия курса.

    Args:
        tariff_id: ID тарифа из поля 'Какой курс куплен' или None

    Returns:
        str: Суффикс для названия курса (пустая строка если тариф не найден или None)
    """
    if tariff_id is None:
        return ""
    
    mapping = get_tariff_suffix_mapping()
    return mapping.get(tariff_id, "")


def get_course_name_text_mapping() -> dict[str, str]:
    """
    Возвращает маппинг текстовых названий курсов из amoCRM в названия для платформы.

    Ключ: название курса из webhook amoCRM
    Значение: название курса для платформы

    Returns:
        dict[str, str]: Словарь маппинга названий курсов
    """
    return {
        # Полугодовые курсы
        "Полугодовой 2к26 ОГЭ": "Полугодовой 2к26 9 класс",
        "Полугодовой 2к26 10 класс": "Полугодовой 2к26 10 класс",
        "Полугодовой 2к26 11 класс": "Полугодовой 2к26 11 класс",
        "Весенний курс 2к26 ЕГЭ 11 класс": "Весенний курс 2к26 11 класс",
        "Весенний курс 2к26 ЕГЭ 10 класс": "Весенний курс 2к26 10 класс",
        "Весенний курс 2к26 ОГЭ": "Весенний курс 2к26 9 класс",

        # Математика
        "Математика 7 класс 2к26": "Математика 7 класс",
        "Математика 8 класс 2к26": "Математика 8 класс",

        # Скорая помощь
        "Скорая помощь 2к26 10 класс": "Скорая помощь 2к26 10 класс",
        "Скорая помощь 2к26 11 класс": "Скорая помощь 2к26 11 класс",
        "Скорая помощь 2к26 ОГЭ": "Скорая помощь 2к26 9 класс",

    }


def map_course_name_text(course_name_from_amo: str) -> str:
    """
    Преобразовать текстовое название курса из amoCRM в название для платформы.

    Args:
        course_name_from_amo: Название курса из webhook amoCRM

    Returns:
        str: Название курса для платформы (если маппинг найден) или исходное название

    Raises:
        ValueError: Если маппинг для курса не найден
    """
    mapping = get_course_name_text_mapping()

    if course_name_from_amo not in mapping:
        raise ValueError(
            f"Маппинг для курса '{course_name_from_amo}' не найден. "
            f"Доступные курсы: {', '.join(mapping.keys())}"
        )

    return mapping[course_name_from_amo]
