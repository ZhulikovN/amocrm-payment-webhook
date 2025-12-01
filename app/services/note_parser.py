"""Парсер примечаний от платежных систем в amoCRM."""

import re


def is_payment_note(note_text: str) -> bool:
    """
    Проверяет, является ли примечание уведомлением об оплате.

    Примеры примечаний об оплате:
    - "Заказ №5432345 [8490.00 RUB] ✓ Платёж получен"
    - "Платёж получен ✓"
    - "Payment received"

    Args:
        note_text: Текст примечания

    Returns:
        bool: True если это примечание об оплате
    """
    if not note_text:
        return False

    payment_markers = [
        "платёж получен",
        "платеж получен",
        "payment received",
        "оплачено",
        "paid",
    ]

    note_lower = note_text.lower()

    for marker in payment_markers:
        if marker in note_lower:
            return True

    if "✓" in note_text and ("заказ" in note_lower or "order" in note_lower):
        return True

    return False


def extract_payment_amount(note_text: str) -> float | None:
    """
    Извлекает сумму платежа из текста примечания.

    Примеры:
    - "Заказ №5432345 [8490.00 RUB] ✓ Платёж получен" → 8490.00
    - "Платёж 5000 рублей получен" → 5000.0

    Args:
        note_text: Текст примечания

    Returns:
        float | None: Сумма платежа или None если не найдена
    """
    if not note_text:
        return None

    patterns = [
        r"\[(\d+(?:\.\d+)?)\s*(?:RUB|руб|₽)\]",
        r"(\d+(?:\.\d+)?)\s*(?:RUB|руб|рублей|₽)",
    ]

    for pattern in patterns:
        match = re.search(pattern, note_text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue

    return None


def extract_order_number(note_text: str) -> str | None:
    """
    Извлекает номер заказа из текста примечания.

    Примеры:
    - "Заказ №5432345 [8490.00 RUB] ✓ Платёж получен" → "5432345"

    Args:
        note_text: Текст примечания

    Returns:
        str | None: Номер заказа или None если не найден
    """
    if not note_text:
        return None

    patterns = [
        r"заказ\s*№?\s*(\d+)",
        r"order\s*#?\s*(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, note_text, re.IGNORECASE)
        if match:
            return match.group(1)

    return None
