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
        except ValueError:
            raise ValueError(f"Маппинг для предмета с ID {subject_id} не найден")

    return mapping[subject_id]
