import sys
import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import ChatMemberUpdated, ChatJoinRequest
from config import Config
from helper.database import db
from pyrogram.errors import FloodWait

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_welcome_message(bot, user_id, chat_title, welcome_message, media_file):
    """Send a welcome message with optional media file to the user."""
    try:
        if media_file:
            try:
                await bot.send_photo(chat_id=user_id, photo=media_file, caption=welcome_message.format(user_id=user_id, title=chat_title))
            except:
                try:
                    await bot.send_animation(chat_id=user_id, animation=media_file, caption=welcome_message.format(user_id=user_id, title=chat_title))
                except:
                    await bot.send_video(chat_id=user_id, video=media_file, caption=welcome_message.format(user_id=user_id, title=chat_title))
        else:
            await bot.send_message(chat_id=user_id, text=welcome_message.format(user_id=user_id, title=chat_title))
    except Exception as e:
        logger.error(f"Failed to send welcome message to {user_id}: {e}")

async def approve_func(bot, message):
    """Approve chat join requests and send a welcome message if configured."""
    try:
        chat = message.chat
        user = message.from_user
        await bot.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        await db.add_appro_user(bot, message)

        if await db.get_bool_welc(Config.ADMIN):
            welcome_message = await db.get_welcome(Config.ADMIN) or Config.DEFAULT_WELCOME_MSG
            media_file = await db.get_welc_file(Config.ADMIN)
            await send_welcome_message(bot, user.id, chat.title, welcome_message, media_file)
    except Exception as e:
        logger.error(f"Error approving join request for {user.id} in {chat.id}: {e}")

@Client.on_chat_join_request(filters.group)
async def handle_auto_accept(bot: Client, message: ChatJoinRequest):
    """Automatically approve chat join requests based on admin configuration."""
    try:
        if await db.get_bool_auto_accept(Config.ADMIN) and await db.get_admin_channels().get(str(message.chat.id)):
            await approve_func(bot, message)
    except FloodWait as e:
        logger.warning(f"FloodWait encountered: {e}")
        await asyncio.sleep(e.value)
        await approve_func(bot, message)
    except Exception as e:
        logger.error(f"Error handling join request: {e}")

@Client.on_chat_member_updated()
async def handle_chat_member_update(bot: Client, update: ChatMemberUpdated):
    """Handle updates to chat member statuses, including bot promotions and demotions."""
    try:
        if update.old_chat_member and update.old_chat_member.user.id == bot.me.id:
            chat_id = update.chat.id
            if update.old_chat_member.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.ADMINISTRATOR]:
                await db.remove_channel(Config.ADMIN, chat_id)
                await db.remove_admin_channel(str(chat_id))

        if update.new_chat_member.user.id == bot.me.id:
            chat_id = update.chat.id
            if update.new_chat_member.status == enums.ChatMemberStatus.ADMINISTRATOR:
                await db.set_channel(Config.ADMIN, chat_id)
                await db.set_admin_channel(chat_id, True)
    except Exception as e:
        logger.error(f"Error handling chat member update: {e}")

if __name__ == "__main__":
    app = Client(
        "approver",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN
    )

    logger.info("Bot is starting...")
    app.run()
