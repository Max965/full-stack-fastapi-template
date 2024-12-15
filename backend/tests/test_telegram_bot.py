import pytest
from app.telegram_bot import TelegramClient
from app.models.task import Task
from uuid import uuid4

@pytest.fixture
def telegram_client():
    return TelegramClient(token="YOUR_TELEGRAM_BOT_TOKEN")

@pytest.fixture
def sample_task():
    return Task(
        id=uuid4(),
        title="Test Task",
        description="This is a test task.",
        status="TODO",
        priority="MEDIUM",
        owner_id=uuid4()  # Replace with a valid owner_id if needed
    )

def test_send_task(telegram_client, sample_task):
    chat_id = "YOUR_CHAT_ID"  # Replace with your chat ID
    telegram_client.send_task(chat_id, sample_task)
    # You can add assertions here to verify the message was sent 