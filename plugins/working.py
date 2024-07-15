import sys
import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import ChatMemberUpdated, ChatJoinRequest, Message
from config import Config
from helper.database import db
from pyrogram.errors import FloodWait, PeerIdInvalid

# Set up logging
logging.basicConfig(level=logging.ERROR)

# Initialize the bot client
app = Client("my_bot")

# Dummy functions for context
def add_group(group_id):
    # Add group_id to the database
    pass

def add_user(user_id):
    # Add user_id to the database
    pass

@app.on_chat_join_request(filters.group | filters.channel & ~filters.private)
async def approve(client: Client, message: ChatJoinRequest):
    op = message.chat
    user = message.from_user
    try:
        add_group(op.id)
        await client.approve_chat_join_request(op.id, user.id)
        await client.send_message(user.id, f"**Hello {user.mention}!\nWelcome to {op.title}**")
        add_user(user.id)
    except PeerIdInvalid:
        logging.error("User hasn't started the bot (means group).")
    except Exception as err:
        logging.error(f"Error: {err}")

@Client.on_chat_join_request(filters.group | filters.channel)
async def handle_auto_accept(client: Client, message: ChatJoinRequest):
    admin_permission = await db.get_bool_auto_accept(Config.ADMIN)
    admin_channel_permission = await db.get_admin_channels()
    channel_permission = admin_channel_permission.get(f'{message.chat.id}', False)

    if admin_permission and channel_permission:
        try:
            await approve(client, message)
        except FloodWait as e:
            logging.warning(f"FloodWait error: {e}. Retrying after {e.x} seconds.")
            await asyncio.sleep(e.x)
            await approve(client, message)

@Client.on_chat_member_updated()
async def handle_chat(client: Client, update: ChatMemberUpdated):
    left_user = update.old_chat_member
    if left_user:
        try:
            bool_leave = await db.get_bool_leav(Config.ADMIN)
            if bool_leave:
                leave_message = await db.get_leave(Config.ADMIN)
                photo_or_video_file = await db.get_leav_file(Config.ADMIN)
                if photo_or_video_file:
                    try:
                        await client.send_photo(
                            chat_id=left_user.user.id, 
                            photo=photo_or_video_file, 
                            caption=leave_message.format(user=left_user.user.mention, title=update.chat.title) if leave_message else Config.DEFAULT_LEAVE_MSG.format(user=left_user.user.mention, title=update.chat.title)
                        )
                    except:
                        await client.send_animation(
                            chat_id=left_user.user.id, 
                            animation=photo_or_video_file, 
                            caption=leave_message.format(user=left_user.user.mention, title=update.chat.title) if leave_message else Config.DEFAULT_LEAVE_MSG.format(user=left_user.user.mention, title=update.chat.title)
                        )
                else:
                    await client.send_message(
                        chat_id=left_user.user.id, 
                        text=leave_message.format(user=left_user.user.mention, title=update.chat.title) if leave_message else Config.DEFAULT_LEAVE_MSG.format(user=left_user.user.mention, title=update.chat.title)
                    )
        except Exception as err:
            logging.error(f"Error handling chat member update: {err}")

    try:
        if update.new_chat_member.user.id == client.me.id:
            chat_id = update.chat.id
            if update.new_chat_member.status == enums.ChatMemberStatus.ADMINISTR
