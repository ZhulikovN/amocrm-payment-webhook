"""Тесты для маппинга предметов из amoCRM в subject_designation платформы."""

import pytest

from app.config.subject_mapping import (
    get_class_mapping,
    get_subject_mapping,
    get_subject_name_by_id,
    map_class_to_number,
    map_subject_to_designation,
)
from app.settings import settings


class TestGetSubjectMapping:
    """Тесты для функции get_subject_mapping."""

    def test_mapping_contains_all_subjects(self) -> None:
        """Тест что маппинг содержит все 15 предметов."""
        mapping = get_subject_mapping()
        assert len(mapping) == 15

    def test_mapping_keys_are_integers(self) -> None:
        """Тест что ключи маппинга - целые числа (ID из amoCRM)."""
        mapping = get_subject_mapping()
        for key in mapping.keys():
            assert isinstance(key, int)

    def test_mapping_values_are_strings(self) -> None:
        """Тест что значения маппинга - строки (subject_designation)."""
        mapping = get_subject_mapping()
        for value in mapping.values():
            assert isinstance(value, str)


class TestMapSubjectToDesignation:
    """Тесты для функции map_subject_to_designation."""

    def test_map_obshchestvo_to_social(self) -> None:
        """Тест маппинга Обществознание → social."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_OBSHCHESTVO) == "social"

    def test_map_english(self) -> None:
        """Тест маппинга Английский язык → english."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_ENGLISH) == "english"

    def test_map_history(self) -> None:
        """Тест маппинга История → history."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_HISTORY) == "history"

    def test_map_russian(self) -> None:
        """Тест маппинга Русский → russian."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_RUSSIAN) == "russian"

    def test_map_physics(self) -> None:
        """Тест маппинга Физика → physics."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_PHYSICS) == "physics"

    def test_map_chemistry(self) -> None:
        """Тест маппинга Химия → chemistry."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_CHEMISTRY) == "chemistry"

    def test_map_literature(self) -> None:
        """Тест маппинга Литература → literature."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_LITERATURE) == "literature"

    def test_map_math_prof_masha(self) -> None:
        """Тест маппинга Профиль Маша → maths."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_MATH_PROF_MASHA) == "maths"

    def test_map_math_base(self) -> None:
        """Тест маппинга База матем → maths-base."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_MATH_BASE) == "maths-base"

    def test_map_biology_zhenya(self) -> None:
        """Тест маппинга Биология Женя → biology."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_BIOLOGY_ZHENYA) == "biology"

    def test_map_informatics(self) -> None:
        """Тест маппинга Информатика → informatics."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_INFORMATICS) == "informatics"

    def test_map_math_prof_sasha(self) -> None:
        """Тест маппинга Профиль Саша → maths2."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_MATH_PROF_SASHA) == "maths2"

    def test_map_biology_gelya(self) -> None:
        """Тест маппинга Биология Геля → biology2."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_BIOLOGY_GELYA) == "biology2"

    def test_map_math_7_8(self) -> None:
        """Тест маппинга Математика 7-8 класс → middle_math."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_MATH_7_8) == "middle_math"

    def test_map_math_oge(self) -> None:
        """Тест маппинга Математика ОГЭ → maths-oge."""
        assert map_subject_to_designation(settings.AMO_SUBJECT_MATH_OGE) == "maths-oge"

    def test_map_unknown_subject_raises_error(self) -> None:
        """Тест что неизвестный ID предмета вызывает ошибку."""
        with pytest.raises(ValueError, match="Маппинг для предмета"):
            map_subject_to_designation(999999)


class TestGetSubjectNameById:
    """Тесты для функции get_subject_name_by_id."""

    def test_get_name_obshchestvo(self) -> None:
        """Тест получения названия для Обществознание."""
        assert get_subject_name_by_id(settings.AMO_SUBJECT_OBSHCHESTVO) == "Обществознание"

    def test_get_name_math_prof_masha(self) -> None:
        """Тест получения названия для Профиль Маша."""
        assert get_subject_name_by_id(settings.AMO_SUBJECT_MATH_PROF_MASHA) == "Профиль Маша"

    def test_get_name_biology_gelya(self) -> None:
        """Тест получения названия для Биология Геля."""
        assert get_subject_name_by_id(settings.AMO_SUBJECT_BIOLOGY_GELYA) == "Биология Геля"

    def test_get_name_math_7_8(self) -> None:
        """Тест получения названия для Математика 7-8 класс."""
        assert get_subject_name_by_id(settings.AMO_SUBJECT_MATH_7_8) == "Математика 7-8 класс"

    def test_get_name_math_oge(self) -> None:
        """Тест получения названия для Математика ОГЭ."""
        assert get_subject_name_by_id(settings.AMO_SUBJECT_MATH_OGE) == "Математика ОГЭ"

    def test_get_name_unknown_id_raises_error(self) -> None:
        """Тест что неизвестный ID вызывает ошибку."""
        with pytest.raises(ValueError, match="Неизвестный ID предмета"):
            get_subject_name_by_id(999999)


class TestGetClassMapping:
    """Тесты для функции get_class_mapping."""

    def test_mapping_contains_all_classes(self) -> None:
        """Тест что маппинг содержит все 9 вариантов классов."""
        mapping = get_class_mapping()
        assert len(mapping) == 9

    def test_mapping_keys_are_integers(self) -> None:
        """Тест что ключи маппинга - целые числа (ID из amoCRM)."""
        mapping = get_class_mapping()
        for key in mapping.keys():
            assert isinstance(key, int)

    def test_mapping_values_are_integers(self) -> None:
        """Тест что значения маппинга - целые числа (номера классов)."""
        mapping = get_class_mapping()
        for value in mapping.values():
            assert isinstance(value, int)
            assert 1 <= value <= 11


class TestMapClassToNumber:
    """Тесты для функции map_class_to_number."""

    def test_map_class_5_6(self) -> None:
        """Тест маппинга 5-6 класс → 6."""
        assert map_class_to_number(settings.AMO_CLASS_5_6) == 6

    def test_map_class_7(self) -> None:
        """Тест маппинга 7 класс → 7."""
        assert map_class_to_number(settings.AMO_CLASS_7) == 7

    def test_map_class_8(self) -> None:
        """Тест маппинга 8 класс → 8."""
        assert map_class_to_number(settings.AMO_CLASS_8) == 8

    def test_map_class_9(self) -> None:
        """Тест маппинга 9 класс → 9."""
        assert map_class_to_number(settings.AMO_CLASS_9) == 9

    def test_map_class_10(self) -> None:
        """Тест маппинга 10 класс → 10."""
        assert map_class_to_number(settings.AMO_CLASS_10) == 10

    def test_map_class_11(self) -> None:
        """Тест маппинга 11 класс → 11."""
        assert map_class_to_number(settings.AMO_CLASS_11) == 11

    def test_map_class_younger_9(self) -> None:
        """Тест маппинга Младше 9 класса → 8."""
        assert map_class_to_number(settings.AMO_CLASS_YOUNGER_9) == 8

    def test_map_class_university(self) -> None:
        """Тест маппинга Университет → 11."""
        assert map_class_to_number(settings.AMO_CLASS_UNIVERSITY) == 11

    def test_map_class_not_student(self) -> None:
        """Тест маппинга Не ученик → 11."""
        assert map_class_to_number(settings.AMO_CLASS_NOT_STUDENT) == 11

    def test_map_unknown_class_raises_error(self) -> None:
        """Тест что неизвестный ID класса вызывает ошибку."""
        with pytest.raises(ValueError, match="Маппинг для класса"):
            map_class_to_number(999999)

