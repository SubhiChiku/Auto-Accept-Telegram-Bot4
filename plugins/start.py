from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from helper.database import db
from config import Config, TxT
from helper.utils import (
    OnWelcBtn,
    OnLeavBtn,
    OffWelcBtn,
    OffLeavBtn,
    OnAutoacceptBtn,
    OffAutoacceptBtn,
)


@Client.on_message(filters.private & filters.command("start"))
async def handle_start(bot: Client, message: Message):
    SnowDev = await message.reply_text(text="**Please Wait...**", reply_to_message_id=message.id)
    await db.add_user(b=bot, m=message)
    text = f"Hi, {message.from_user.mention}\n\n I'm Auto Accept Bot. I can accept users from any channel and group if you make me admin there."
    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="ᴅᴇᴠᴇʟᴏᴘᴇʀ 👨‍💻", url="https://t.me/Snowball_Official")],
            [InlineKeyboardButton("ʜᴇʟᴘ ❗", callback_data="help")],
        ]
    )

    try:
        if Config.START_PIC:
            await SnowDev.delete()
            await message.reply_photo(photo=Config.START_PIC, caption=text, reply_markup=reply_markup)
        else:
            await SnowDev.edit(text=text, reply_markup=reply_markup)
    except Exception as e:
        await SnowDev.edit(text=f"Error: {e}")


@Client.on_message(filters.private & filters.command("set_welcome") & filters.user(Config.ADMIN))
async def set_welcome_msg(bot: Client, message: Message):
    welcome_msg = message.reply_to_message
    if not welcome_msg:
        await message.reply_text("Invalid Command!\n⚠️ Format ➜ `Hey, {user} Welcome to {title}` \n\n **Reply to a message**")
        return

    SnowDev = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)

    try:
        if welcome_msg.photo or welcome_msg.video or welcome_msg.animation:
            await db.set_welcome(message.from_user.id, welcome_msg.caption)
            file_id = welcome_msg.photo.file_id if welcome_msg.photo else welcome_msg.video.file_id if welcome_msg.video else welcome_msg.animation.file_id
            await db.set_welc_file(message.from_user.id, file_id)
        else:
            await db.set_welcome(message.from_user.id, welcome_msg.text)
            await db.set_welc_file(message.from_user.id, None)
        await SnowDev.edit("Successfully set your welcome message ✅")
    except Exception as e:
        await SnowDev.edit(f"Error: {e}")


@Client.on_message(filters.private & filters.command("set_leave") & filters.user(Config.ADMIN))
async def set_leave_msg(bot: Client, message: Message):
    leave_msg = message.reply_to_message
    if not leave_msg:
        await message.reply_text("Invalid Command!\n⚠️ Format ➜ `Hey, {user} Bye, see you again from {title}` \n\n **Reply to a message**")
        return

    SnowDev = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)

    try:
        if leave_msg.photo or leave_msg.video or leave_msg.animation:
            await db.set_leave(message.from_user.id, leave_msg.caption)
            file_id = leave_msg.photo.file_id if leave_msg.photo else leave_msg.video.file_id if leave_msg.video else leave_msg.animation.file_id
            await db.set_leav_file(message.from_user.id, file_id)
        else:
            await db.set_leave(message.from_user.id, leave_msg.text)
            await db.set_leav_file(message.from_user.id, None)
        await SnowDev.edit("Successfully set your leave message ✅")
    except Exception as e:
        await SnowDev.edit(f"Error: {e}")


@Client.on_message(filters.private & filters.command('auto_approves') & filters.user(Config.ADMIN))
async def handle_auto_approves(bot: Client, message: Message):
    SnowDev = await message.reply_text('**Please Wait...**', reply_to_message_id=message.id)
    btns = []

    try:
        db_channels = await db.get_admin_channels()
        for key, value in db_channels.items():
            chnl = await bot.get_chat(key)
            btn_text = f'{chnl.title} {"✅" if value else "❌"}'
            btns.append([InlineKeyboardButton(btn_text, callback_data=f'autoapprove_{key}')])

        await SnowDev.edit("**Here are the channels where I'm admin and you can toggle the auto accept functionality.**", reply_markup=InlineKeyboardMarkup(btns))
    except Exception as e:
        await SnowDev.edit(f"Error: {e}")


@Client.on_message(filters.private & filters.command('option') & filters.user(Config.ADMIN))
async def set_bool_welc(bot: Client, message: Message):
    SnowDev = await message.reply_text("**Please Wait...**", reply_to_message_id=message.id)
    user_id = message.from_user.id

    bool_welc = await db.get_bool_welc(user_id)
    bool_leav = await db.get_bool_leav(user_id)
    bool_auto_accept = await db.get_bool_auto_accept(user_id)

    welc_button_row = [OnWelcBtn if bool_welc else OffWelcBtn, OnLeavBtn if bool_leav else OffLeavBtn]
    autoaccept_button_row = [OnAutoacceptBtn if bool_auto_accept else OffAutoacceptBtn]

    text = "Click the button below to toggle Welcome, Leaving Message, and Auto Accept."
    reply_markup = InlineKeyboardMarkup([welc_button_row, autoaccept_button_row])

    await SnowDev.edit(text=text, reply_markup=reply_markup)


@Client.on_callback_query()
async def handle_CallbackQuery(bot: Client, query: CallbackQuery):
    data = query.data

    if data.startswith('autoapprove_'):
        await toggle_autoapprove(bot, query)
    elif data.startswith('welc'):
        await toggle_bool_welc(query)
    elif data.startswith('leav'):
        await toggle_bool_leav(query)
    elif data.startswith('autoaccept'):
        await toggle_bool_autoaccept(query)
    elif data == 'help':
        await query.message.edit(TxT.HELP_MSG, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('✘ Close ✘', callback_data='close')]]))
    elif data == 'close':
        await query.message.delete()


async def toggle_autoapprove(bot: Client, query: CallbackQuery):
    channel_id = query.data.split('_')[1]
    text = "**Here are the channels where I'm admin and you can toggle the auto accept functionality.**"
    btn = []

    try:
        db_channels = await db.get_admin_channels()
        for key, value in db_channels.items():
            channel = await bot.get_chat(key)
            if key == channel_id:
                new_value = not value
                await db.update_admin_channel(channel_id, new_value)
                btn_text = f'{channel.title} {"✅" if new_value else "❌"}'
            else:
                btn_text = f'{channel.title} {"✅" if value else "❌"}'
            btn.append([InlineKeyboardButton(btn_text, callback_data=f'autoapprove_{key}')])
        await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup(btn))
    except Exception as e:
        await query.message.edit(f"Error: {e}")


async def toggle_bool_welc(query: CallbackQuery):
    text = "Click the button below to toggle Welcome, Leaving Message, and Auto Accept."
    boolean = query.data.split('-')[1] == 'on'
    await db.set_bool_welc(query.from_user.id, not boolean)
    await update_option_message(query, text)


async def toggle_bool_leav(query: CallbackQuery):
    text = "Click the button below to toggle Welcome, Leaving Message, and Auto Accept."
    boolean = query.data.split('-')[1] == 'on'
    await db.set_bool_leav(query.from_user.id, not boolean)
    await update_option_message(query, text)


async def toggle_bool_autoaccept(query: CallbackQuery):
    text = "Click the button below to toggle Welcome, Leaving Message, and Auto Accept."
    boolean = query.data.split('-')[1] == 'on'
    await db.set_bool_auto_accept(query.from_user.id, not boolean)
    await update_option_message(query, text)


async def update_option_message(query: CallbackQuery, text: str):
    user_id = query.from_user.id
    bool_welc = await db.get_bool_welc(user_id)
    bool_leav = await db.get_bool_leav(user_id)
    bool_auto_accept = await db.get_bool_auto_accept(user_id)

    welc_button_row = [OnWelcBtn if bool_welc else OffWelcBtn, OnLeavBtn if bool_leav else OffLeavBtn]
    autoaccept_button_row = [OnAutoacceptBtn if bool_auto_accept else OffAutoacceptBtn]

    reply_markup = InlineKeyboardMarkup([welc_button_row, autoaccept_button_row])
    await query.message.edit(text=text, reply_markup=reply_markup)
