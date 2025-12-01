"""Интеграционные тесты для AmoCRM клиента."""
# poetry run pytest ./tests/test_amocrm_client/test_amocrm_client.py -v -m integration -s
import pytest

from app.services.amocrm_client import AmoCRMClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_lead_with_contact_real_data() -> None:
    """Тест получения реальной сделки 38743359 с контактом из amoCRM."""
    client = AmoCRMClient()

    lead_id = 38743359

    result = await client.get_lead_with_contact(lead_id)

    assert "lead" in result
    assert "contact" in result

    lead = result["lead"]
    contact = result["contact"]

    assert lead["id"] == lead_id
    assert "name" in lead
    assert "custom_fields_values" in lead

    assert "id" in contact
    assert "name" in contact
    assert "custom_fields_values" in contact

    print(f"\n✓ Lead ID: {lead['id']}")
    print(f"✓ Lead name: {lead['name']}")
    print(f"✓ Contact ID: {contact['id']}")
    print(f"✓ Contact name: {contact['name']}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_extract_lead_data_real_data() -> None:
    """Тест извлечения данных из реальной сделки 38743359."""
    client = AmoCRMClient()

    lead_id = 38743359

    result = await client.get_lead_with_contact(lead_id)
    lead = result["lead"]
    contact = result["contact"]

    extracted = client.extract_lead_data(lead, contact)

    assert extracted["lead_id"] == lead_id
    assert "class_enum_id" in extracted
    assert "subjects_enum_ids" in extracted
    assert "direction_enum_id" in extracted
    assert "purchased_course_enum_ids" in extracted
    assert "contact_name" in extracted
    assert "contact_phone" in extracted
    assert "contact_email" in extracted

    assert isinstance(extracted["subjects_enum_ids"], list)
    assert isinstance(extracted["purchased_course_enum_ids"], list)

    print(f"\n✓ Lead ID: {extracted['lead_id']}")
    print(f"✓ Class enum ID: {extracted['class_enum_id']}")
    print(f"✓ Subjects enum IDs: {extracted['subjects_enum_ids']}")
    print(f"✓ Direction enum ID: {extracted['direction_enum_id']}")
    print(f"✓ Purchased course enum IDs: {extracted['purchased_course_enum_ids']}")
    print(f"✓ Contact name: {extracted['contact_name']}")
    print(f"✓ Contact phone: {extracted['contact_phone']}")
    print(f"✓ Contact email: {extracted['contact_email']}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_parse_custom_fields() -> None:
    """Тест парсинга кастомных полей."""
    client = AmoCRMClient()

    custom_fields = [
        {"field_id": 123, "values": [{"value": "test_value"}]},
        {"field_id": 456, "values": [{"enum_id": 789}]},
        {"field_id": 999, "values": [{"enum_id": 111}, {"enum_id": 222}]},
    ]

    result = client._parse_custom_fields(custom_fields)

    assert result[123] == "test_value"
    assert result[456] == 789
    assert result[999] == [111, 222]

    print(f"\n✓ Parsed fields: {result}")

