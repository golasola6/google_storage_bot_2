from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest
from database.database import db
from config import * 
from datetime import datetime, timedelta
import pytz
import logging
import asyncio
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import *
#5 => verification_steps ! [Youtube@LazyDeveloperr]
logger = logging.getLogger(__name__)
import pytz  # Make sure to handle timezone correctly
from utils import temp 
from helper_func import subscribed, encode, decode, get_messages
from pyrogram.errors import FloodWait,ChatAdminRequired, UserIsBlocked, InputUserDeactivated, PeerIdInvalid
from start import delete_files

@Client.on_chat_join_request(filters.chat(temp.ASSIGNED_CHANNEL))  # Fetch channels dynamically
async def join_reqs(client, message: ChatJoinRequest):
    try:
        user_id = message.from_user.id
        file_id = temp.FILE_ID[user_id]["LAZY_FILE"]
        print(f"file id in req  = {file_id}")
        # print(f"base64_string on start : {base64_string}")
        string = await decode(file_id)
        argument = string.split("-")
        ids = []
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
            except Exception as e:
                print(f"Error decoding IDs: {e}")
                return

        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except Exception as e:
                print(f"Error decoding ID: {e}")
                return

        temp_msg = await message.reply("Wait A Sec..")
        print(f"ids -=> {ids}")
        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await message.reply_text("Something Went Wrong..!")
            print(f"Error getting messages: {e}")
            return
        finally:
            await temp_msg.delete()

        lazy_msgs = []  # List to keep track of sent messages

        for msg in messages:
            caption = (CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, 
                                             filename=msg.document.file_name) if bool(CUSTOM_CAPTION) and bool(msg.document)
                       else ("" if not msg.caption else msg.caption.html))

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, 
                                            reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                lazy_msgs.append(copied_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, 
                                            reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                lazy_msgs.append(copied_msg)
            except Exception as e:
                print(f"Failed to send message: {e}")
                pass

        k = await client.send_message(chat_id=message.from_user.id, 
                                      text=f"<b><i>This File is deleting automatically in {file_auto_delete}. Forward in your Saved Messages..!</i></b>")

        # Schedule the file deletion
        asyncio.create_task(delete_files(lazy_msgs, client, k))
    except Exception as lazydeveloper:
        logging.info(f"Error: {lazydeveloper}")


@Client.on_message(filters.command("delreq") & filters.private & filters.user(ADMINS))
async def del_requests(client, message):
    await db.del_join_req()    
    await message.reply("<b>⚙ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴄʜᴀɴɴᴇʟ ʟᴇғᴛ ᴜꜱᴇʀꜱ ᴅᴇʟᴇᴛᴇᴅ</b>")
