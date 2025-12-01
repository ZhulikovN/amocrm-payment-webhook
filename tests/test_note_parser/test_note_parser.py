"""Тесты для модуля парсинга примечаний от платежных систем."""

from app.services.note_parser import extract_order_number, extract_payment_amount, is_payment_note


class TestIsPaymentNote:
    """Тесты для функции is_payment_note."""

    def test_payment_note_tinkoff_format(self) -> None:
        """Тест распознавания примечания от Тинькофф."""
        note = "Заказ №5432345 [8490.00 RUB]\n✓ Платёж получен"
        assert is_payment_note(note) is True

    def test_payment_note_simple_format(self) -> None:
        """Тест распознавания простого примечания об оплате."""
        note = "Платёж получен"
        assert is_payment_note(note) is True

    def test_payment_note_alternative_spelling(self) -> None:
        """Тест распознавания примечания с альтернативным написанием."""
        note = "Платеж получен"
        assert is_payment_note(note) is True

    def test_payment_note_with_checkmark(self) -> None:
        """Тест распознавания примечания с галочкой."""
        note = "✓ Заказ оплачен"
        assert is_payment_note(note) is True

    def test_payment_note_english(self) -> None:
        """Тест распознавания примечания на английском."""
        note = "Payment received"
        assert is_payment_note(note) is True

    def test_not_payment_note_regular_text(self) -> None:
        """Тест что обычное примечание не распознается как платежное."""
        note = "проблемы с амо"
        assert is_payment_note(note) is False

    def test_not_payment_note_call_json(self) -> None:
        """Тест что JSON от онлайн-АТС не распознается как платежное."""
        note = '{"PHONE":"79095158362","UNIQ":"e6381519","DURATION":32,"call_status":4}'
        assert is_payment_note(note) is False

    def test_not_payment_note_empty(self) -> None:
        """Тест что пустая строка не является платежным примечанием."""
        assert is_payment_note("") is False

    def test_not_payment_note_none(self) -> None:
        """Тест что None не является платежным примечанием."""
        assert is_payment_note(None) is False  # type: ignore[arg-type]


class TestExtractPaymentAmount:
    """Тесты для функции extract_payment_amount."""

    def test_extract_amount_brackets_rub(self) -> None:
        """Тест извлечения суммы в формате [XXXX.XX RUB]."""
        note = "Заказ №5432345 [8490.00 RUB]\n✓ Платёж получен"
        assert extract_payment_amount(note) == 8490.00

    def test_extract_amount_no_brackets(self) -> None:
        """Тест извлечения суммы без скобок."""
        note = "Платёж 5000 рублей получен"
        assert extract_payment_amount(note) == 5000.0

    def test_extract_amount_rubles_symbol(self) -> None:
        """Тест извлечения суммы с символом рубля."""
        note = "Сумма 1234.56 ₽"
        assert extract_payment_amount(note) == 1234.56

    def test_extract_amount_integer(self) -> None:
        """Тест извлечения целой суммы."""
        note = "Заказ [10000 RUB] оплачен"
        assert extract_payment_amount(note) == 10000.0

    def test_extract_amount_not_found(self) -> None:
        """Тест что возвращается None если сумма не найдена."""
        note = "Платёж получен"
        assert extract_payment_amount(note) is None

    def test_extract_amount_empty(self) -> None:
        """Тест что возвращается None для пустой строки."""
        assert extract_payment_amount("") is None

    def test_extract_amount_none(self) -> None:
        """Тест что возвращается None для None."""
        assert extract_payment_amount(None) is None  # type: ignore[arg-type]


class TestExtractOrderNumber:
    """Тесты для функции extract_order_number."""

    def test_extract_order_number_russian(self) -> None:
        """Тест извлечения номера заказа на русском."""
        note = "Заказ №5432345 [8490.00 RUB]\n✓ Платёж получен"
        assert extract_order_number(note) == "5432345"

    def test_extract_order_number_english(self) -> None:
        """Тест извлечения номера заказа на английском."""
        note = "Order #12345 paid"
        assert extract_order_number(note) == "12345"

    def test_extract_order_number_no_hash(self) -> None:
        """Тест извлечения номера заказа без символа #."""
        note = "Заказ 999888 оплачен"
        assert extract_order_number(note) == "999888"

    def test_extract_order_number_not_found(self) -> None:
        """Тест что возвращается None если номер не найден."""
        note = "Платёж получен"
        assert extract_order_number(note) is None

    def test_extract_order_number_empty(self) -> None:
        """Тест что возвращается None для пустой строки."""
        assert extract_order_number("") is None

    def test_extract_order_number_none(self) -> None:
        """Тест что возвращается None для None."""
        assert extract_order_number(None) is None  # type: ignore[arg-type]

