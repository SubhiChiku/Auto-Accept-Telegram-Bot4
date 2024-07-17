import os
import sys
import time
import asyncio
import logging
import datetime
from config import Config
from helper.database import db
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the user client
user = Client(name="User", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.SESSION)


@Client.on_message(filters.command(["stats", "status"]) & filters.user(Config.ADMIN))
async def get_stats(bot, message):
    total_users = await db.total_users_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - Config.BOT_UPTIME))
    start_t = time.time()
    st = await message.reply('**Accessing the details...**')
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await st.edit(text=f"**--Bot Status--** \n\n**⌚ Bot Uptime:** {uptime} \n**🐌 Current Ping:** `{time_taken_s:.3f} ms` \n**👭 Total Users:** `{total_users}`")


@Client.on_message(filters.private & filters.command("restart") & filters.user(Config.ADMIN))
async def restart_bot(bot, message):
    await message.reply_text("🔄 Restarting...")
    os.execl(sys.executable, sys.executable, *sys.argv)


@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast_handler(bot: Client, message: Message):
    await bot.send_message(Config.LOG_CHANNEL, f"{message.from_user.mention} or {message.from_user.id} has started the broadcast...")
    all_users = await db.get_all_users()
    broadcast_msg = message.reply_to_message
    sts_msg = await message.reply_text("Broadcast started...")
    done, failed, success = 0, 0, 0
    start_time = time.time()
    total_users = await db.total_users_count()

    async for user in all_users:
        status = await send_msg(user['id'], broadcast_msg)
        if status == 200:
            success += 1
        else:
            failed += 1
        if status == 400:
            await db.delete_user(user['id'])
        done += 1
        if done % 20 == 0:
            await sts_msg.edit(f"Broadcast in progress: \nTotal Users: {total_users} \nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}")

    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"Broadcast completed: \nCompleted in `{completed_in}`.\n\nTotal Users: {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}")


async def send_msg(user_id, message):
    try:
        await message.forward(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_msg(user_id, message)
    except (InputUserDeactivated, UserIsBlocked, PeerIdInvalid):
        logger.info(f"{user_id}: User deactivated or blocked the bot")
        return 400
    except Exception as e:
        logger.error(f"{user_id}: {e}")
        return 500


@Client.on_message(filters.private & filters.command('acceptall') & filters.user(Config.ADMIN))
async def handle_acceptall(bot: Client, message: Message):
    ms = await message.reply_text("**Please wait...**", reply_to_message_id=message.id)
    chat_ids = await db.get_channel(Config.ADMIN)

    if not chat_ids:
        return await ms.edit("**I'm not admin in any channel or group yet!**")

    buttons = [[InlineKeyboardButton(f"{(await bot.get_chat(id)).title} {(await bot.get_chat(id)).type}", callback_data=f'acceptallchat_{id}') for id in chat_ids]]

    await ms.edit("Select a channel or group below where you want to accept pending requests. Below channels or groups I'm admin there", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.command('declineall') & filters.user(Config.ADMIN))
async def handle_declineall(bot: Client, message: Message):
    ms = await message.reply_text("**Please wait...**", reply_to_message_id=message.id)
    chat_ids = await db.get_channel(Config.ADMIN)

    if not chat_ids:
        return await ms.edit("**I'm not admin in any channel or group yet!**")

    buttons = [[InlineKeyboardButton(f"{(await bot.get_chat(id)).title} {(await bot.get_chat(id)).type}", callback_data=f'declineallchat_{id}') for id in chat_ids]]

    await ms.edit("Select a channel or group below where you want to decline pending requests. Below channels or groups I'm admin there", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex('^acceptallchat_'))
async def handle_accept_pending_request(bot: Client, update: CallbackQuery):
    chat_id = update.data.split('_')[1]
    ms = await update.message.edit("**Please wait, accepting the pending requests... ♻️**")
    try:
        while True:
            try:
                await user.approve_all_chat_join_requests(chat_id=chat_id)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                continue
            except Exception as e:
                logger.error(f"Error approving requests for {chat_id}: {e}")
                break
    finally:
        await ms.delete()
        await update.message.reply_text("**Task Completed** ✓ **Approved ✅ All Pending Join Requests**")


@Client.on_callback_query(filters.regex('^declineallchat_'))
async def handle_decline_pending_request(bot: Client, update: CallbackQuery):
    chat_id = update.data.split('_')[1]
    ms = await update.message.edit("**Please wait, declining the pending requests... ♻️**")
    try:
        while True:
            try:
                await user.decline_all_chat_join_requests(chat_id=chat_id)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                continue
            except Exception as e:
                logger.error(f"Error declining requests for {chat_id}: {e}")
                break
    finally:
        await ms.delete()
        await update.message.reply_text("**Task Completed** ✓ **Declined ❌ All Pending Join Requests**")


if __name__ == "__main__":
    app = Client(
        "approver",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN
    )

    logger.info("Bot is starting...")
    app.run()
