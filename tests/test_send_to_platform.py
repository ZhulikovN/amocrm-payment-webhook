import asyncio
import hashlib
import hmac
import json
import logging
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

API_SECRET_KEY="fba089e027a98c7"
PLATFORM_URL="https://pl.el-ed.ru"

async def test_send_to_platform():
    """Отправить тестовые данные на платформу."""
    
    payload = {
        "courses": [
            {
                "name": "Весенний курс 2к26 11 класс Самостоятельный",
                "subject_designation": "russian",
                "cost": 3000,
                "months": 1
            },
            {
                "name": "Весенний курс 2к26 11 класс Самостоятельный",
                "subject_designation": "biology2",
                "cost": 3000,
                "months": 1
            }
        ],
        "first_name": "Иван",
        "last_name": "Иванов",
        "email": "test_2courses@example.com",
        "phone": "89000000002",
        "class": 11,
        "amount": 6000
    }
    
    body_str = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    
    signature = hmac.new(
        API_SECRET_KEY.encode("utf-8"),
        body_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "X-API-KEY": signature,
        "Content-Type": "application/json"
    }
    
    endpoint = f"{PLATFORM_URL}/api/amo/payment/callback"
    
    logger.info("=" * 80)
    logger.info("ОТПРАВКА ТЕСТОВОГО ЗАПРОСА НА ПЛАТФОРМУ")
    logger.info("=" * 80)
    logger.info("Endpoint: %s", endpoint)
    logger.info("=" * 80)
    logger.info("Payload:")
    logger.info(json.dumps(payload, ensure_ascii=False, indent=2))
    logger.info("=" * 80)
    logger.info("Body string (без пробелов):")
    logger.info(body_str)
    logger.info("=" * 80)
    logger.info("X-API-KEY: %s", signature)
    logger.info("API_SECRET_KEY: %s", API_SECRET_KEY)
    logger.info("=" * 80)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                endpoint,
                headers=headers,
                content=body_str
            )
            
            logger.info("=" * 80)
            logger.info("ОТВЕТ ОТ ПЛАТФОРМЫ:")
            logger.info("=" * 80)
            logger.info("Status code: %s", response.status_code)
            logger.info("Response body: %s", response.text)
            logger.info("=" * 80)
            
            if response.status_code == 200:
                logger.info("[SUCCESS] Запрос выполнен успешно")
                return True
            else:
                logger.error("[FAIL] Платформа вернула ошибку: %s", response.status_code)
                return False
                
    except Exception as e:
        logger.error("=" * 80)
        logger.error("[ERROR] Ошибка при отправке: %s", e)
        logger.error("=" * 80)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_send_to_platform())
    sys.exit(0 if success else 1)
