from telegram import Bot
from telegram.error import TelegramError
from app.models.task import Task  # Import your Task model

class TelegramClient:
    def __init__(self, token: str):
        self.bot = Bot(token)

    def send_task(self, chat_id: str, task: Task) -> None:
        message = f"Task: {task.title}\nDescription: {task.description}\nStatus: {task.status}\nPriority: {task.priority}"
        try:
            self.bot.send_message(chat_id=chat_id, text=message)
        except TelegramError as e:
            print(f"Error sending message: {e}")