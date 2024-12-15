import asyncio
import logging
import telegram

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8068170252:AAGS05mnXPev2p4e6BlqLuwSmkZwREzPp_c"

# Define the command handler for /update
async def update_command(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Hello {user.first_name}! You used the /update command.")

# Define a message handler to process all messages
async def echo_message(update: Update, context: CallbackContext):
    text = update.message.text
    await update.message.reply_text(f"You said: {text}")

# Main function to set up the bot
async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("update", update_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
    
    logging.info("Bot is starting...")
    await application.run_polling()
    
if __name__ == "__main__":
    asyncio.run(main())
