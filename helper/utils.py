from datetime import datetime
from pytz import timezone
from config import Config
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
import logging

# Define the inline buttons for various options
OnWelcBtn = InlineKeyboardButton(text='Welcome On ✅', callback_data='welc-on')
OffWelcBtn = InlineKeyboardButton(text='Welcome Off ❌', callback_data='welc-off')
OnLeavBtn = InlineKeyboardButton(text='Leave On ✅', callback_data='leav-on')
OffLeavBtn = InlineKeyboardButton(text='Leave Off ❌', callback_data='leav-off')
OnAutoacceptBtn = InlineKeyboardButton(text='Auto accept On ✅', callback_data='autoaccept-on')
OffAutoacceptBtn = InlineKeyboardButton(text='Auto accept Off ❌', callback_data='autoaccept-off')

# Define the function to send logs
async def send_log(bot: Client, user):
    if Config.LOG_CHANNEL:
        try:
            curr = datetime.now(timezone("Asia/Kolkata"))
            date = curr.strftime('%d %B, %Y')
            time = curr.strftime('%I:%M:%S %p')
            message = (
                f"**--New User Started the Bot--**\n\n"
                f"User: {user.mention}\n"
                f"ID: `{user.id}`\n"
                f"Username: @{user.username}\n\n"
                f"Date: {date}\n"
                f"Time: {time}\n\n"
                f"By: {bot.mention}"
            )
            await bot.send_message(Config.LOG_CHANNEL, message)
        except Exception as e:
            # Log the exception if the message could not be sent
            logging.error(f"Failed to send log message: {e}")

# Example usage
app = Client("my_bot")

@app.on_message(filters.command(["start"]))
async def welcome_message(client, message):
    user = message.from_user
    await send_log(client, user)
    await message.reply("Welcome to the bot!", reply_markup=InlineKeyboardMarkup([[OnWelcBtn, OffWelcBtn]]))

if __name__ == "__main__":
    app.run()
