import os
import sys
import time
import asyncio
import logging
import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from config import Config
from helper.database import db
from pyromod.exceptions import ListenerTimeout

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


user = Client(name="User", api_id=Config.API_ID,
              api_hash=Config.API_HASH, session_string=Config.SESSION)

app = Client("my_bot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)


@app.on_message(filters.command(["stats", "status"]) & filters.user(Config.ADMIN))
async def get_stats(bot, message):
    total_users = await db.total_users_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - Config.BOT_UPTIME))
    start_t = time.time()
    st = await message.reply('**Aᴄᴄᴇꜱꜱɪɴɢ Tʜᴇ Dᴇᴛᴀɪʟꜱ.....**')
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await st.edit(text=f"**--Bᴏᴛ Sᴛᴀᴛᴜꜱ--** \n\n**⌚️ Bᴏᴛ Uᴩᴛɪᴍᴇ:** {uptime} \n**🐌 Cᴜʀʀᴇɴᴛ Pɪɴɢ:** `{time_taken_s:.3f} ᴍꜱ` \n**👭 Tᴏᴛᴀʟ Uꜱᴇʀꜱ:** `{total_users}`")


@app.on_message(filters.private & filters.command("restart") & filters.user(Config.ADMIN))
async def restart_bot(bot, message):
    await message.reply_text("🔄__Rᴇꜱᴛᴀʀᴛɪɴɢ.....__")
    os.execl(sys.executable, sys.executable, *sys.argv)


@app.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast_handler(bot: Client, message: Message):
    await bot.send_message(Config.LOG_CHANNEL, f"{message.from_user.mention} or {message.from_user.id} Iꜱ ꜱᴛᴀʀᴛᴇᴅ ᴛʜᴇ Bʀᴏᴀᴅᴄᴀꜱᴛ......")
    all_users = await db.get_all_users()
    broadcast_msg = message.reply_to_message
    sts_msg = await message.reply_text("Bʀᴏᴀᴅᴄᴀꜱᴛ Sᴛᴀʀᴛᴇᴅ..!")
    done, failed, success = 0, 0, 0
    start_time = time.time()
    total_users = await db.total_users_count()
    async for user in all_users:
        sts = await send_msg(user['id'], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
        if sts == 400:
            await db.delete_user(user['id'])
        done += 1
        if not done % 20:
            await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Iɴ Pʀᴏɢʀᴇꜱꜱ: \nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users} \nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴩʟᴇᴛᴇᴅ: \nCᴏᴍᴩʟᴇᴛᴇᴅ Iɴ `{completed_in}`.\n\nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users}\nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")


async def send_msg(user_id, message):
    try:
        await message.forward(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_msg(user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : Dᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ")
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : Bʟᴏᴄᴋᴇᴅ Tʜᴇ Bᴏᴛ")
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : Uꜱᴇʀ Iᴅ Iɴᴠᴀʟɪᴅ")
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        return 500


@app.on_message(filters.private & filters.command('acceptall') & filters.user(Config.ADMIN))
async def handle_acceptall(bot: Client, message: Message):
    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
    chat_ids = await db.get_channel(Config.ADMIN)

    if not chat_ids:
        return await ms.edit("**I'm not admin in any Channel or Group yet !**")

    button = []
    for id in chat_ids:
        info = await bot.get_chat(id)
        button.append([InlineKeyboardButton(f"{info.title} {str(info.type).split('.')[1]}", callback_data=f'acceptallchat_{id}')])

    await ms.edit("Select Channel or Group Below Where you want to accept pending requests\n\nBelow Channels or Group I'm Admin there", reply_markup=InlineKeyboardMarkup(button))


@app.on_message(filters.private & filters.command('declineall') & filters.user(Config.ADMIN))
async def handle_declineall(bot: Client, message: Message):
    ms = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
    chat_ids = await db.get_channel(Config.ADMIN)

    if not chat_ids:
        return await ms.edit("**I'm not admin in any Channel or Group yet !**")

    button = []
    for id in chat_ids:
        info = await bot.get_chat(id)
        button.append([InlineKeyboardButton(f"{info.title} {str(info.type).split('.')[1]}", callback_data=f'declineallchat_{id}')])

    await ms.edit("Select Channel or Group Below Where you want to decline pending requests\n\nBelow Channels or Group I'm Admin there", reply_markup=InlineKeyboardMarkup(button))


@app.on_callback_query(filters.regex('^acceptallchat_'))
async def handle_accept_pending_request(bot: Client, update: CallbackQuery):
    chat_id = update.data.split('_')[1]
    ms = await update.message.edit("**Please Wait Accepting the pending requests. ♻️**")
    try:
        while True:
            try:
                await user.approve_all_chat_join_requests(chat_id=chat_id)
            except FloodWait as t:
                await asyncio.sleep(t.value)
                await user.approve_all_chat_join_requests(chat_id=chat_id)
            except Exception as e:
                logger.error(f'Error on line {sys.exc_info()[-1].tb_lineno}: {type(e).__name__}, {e}')
                break
        await update.message.reply_text(f"**Task Completed** ✓ **Approved ✅ All Pending Join Request**")
    except:
        await ms.delete()

@Client.on_callback_query(filters.regex('^declineallchat_'))
async def handle_delcine_pending_request(bot: Client, update: CallbackQuery):
    ms = await update.message.edit("**Please Wait Declining all the peding requests. ♻️**")
    chat_id = update.data.split('_')[1]

    try:
        while True:
            try:
                await user.decline_all_chat_join_requests(chat_id=chat_id)
            except FloodWait as t:
                asyncio.sleep(t.value)
                await user.decline_all_chat_join_requests(chat_id=chat_id)
            except:
                pass

    except:
        await ms.delete()
        await update.message.reply_text("**Task Completed** ✓ **Declined ❌ All The Pending Join Request**")
