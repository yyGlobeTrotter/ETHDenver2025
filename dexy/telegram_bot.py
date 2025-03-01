import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext
from telegram.ext import ApplicationBuilder

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Load API keys
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AGENTKIT_API_URL = os.getenv("AGENTKIT_API_URL")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN in .env file")

# Function to query the AgentKit API
def query_agentkit(user_message):
    try:
        response = requests.post(
            f"{AGENTKIT_API_URL}/query",
            json={"message": user_message},
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 200:
            return response.json().get("response", "No response from AgentKit.")
        else:
            return f"AgentKit Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error querying AgentKit: {str(e)}"

# Function to handle user messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    chat_id = update.message.chat_id

    # Log user input
    logging.info(f"User: {user_message}")

    # Get response from AgentKit
    agent_response = query_agentkit(user_message)

    # Send response back to user (await required)
    await context.bot.send_message(chat_id=chat_id, text=f"🤖 Agent Response: {agent_response}")

'''
def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    chat_id = update.message.chat_id

    # Log user input
    logging.info(f"User: {user_message}")

    # Get response from AgentKit
    agent_response = query_agentkit(user_message)

    # Send response back to user
    context.bot.send_message(chat_id=chat_id, text=f"🤖 Agent Response: {agent_response}")
'''

# Function to handle /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("👋 Hello! I'm your amazing sexy dexy trading assistant specializing in risk management. Ask me anything about your portfolio!")

# Main function to start the bot
def main():
    # Initialize bot

    #updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


    # Start polling for messages
    app.run_polling()
    app.idle()

if __name__ == "__main__":
    main()
