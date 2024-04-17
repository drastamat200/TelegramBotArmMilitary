import logging
from datetime import datetime, timedelta
import json
from typing import Dict, Union
import atexit

from telebot import TeleBot, types

# Bot token (replace with your actual token)
BOT_TOKEN = "7183606934:AAF6fTCBTBcsekUL-3dT5KDgQtm30oRxPu4"

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load settings from JSON file
def load_settings() -> Dict[int, Dict[str, Union[str, int, bool]]]:
    try:
        with open("bot_settings.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save settings to JSON file
def save_settings(settings: Dict[int, Dict[str, Union[str, int, bool]]]):
    # Update the settings with the current welcome message before saving
    for chat_id, chat_settings in settings.items():
        if "welcome_message" in chat_settings:
            welcome_message = chat_settings["welcome_message"]
            chat_settings["welcome_message"] = welcome_message

    with open("bot_settings.json", "w") as f:
        json.dump(settings, f)

# Initialize bot and load settings
bot = TeleBot(BOT_TOKEN)
settings = load_settings()

# Function to save settings before bot shutdown
def save_settings_before_shutdown():
    # Update the settings with the current welcome message before saving
    for chat_id, chat_settings in settings.items():
        if "welcome_message" in chat_settings:
            welcome_message = chat_settings["welcome_message"]
            chat_settings["welcome_message"] = welcome_message

    save_settings(settings)

# Register save_settings_before_shutdown function to be called when the program exits
atexit.register(save_settings_before_shutdown)

# Function to check if bot is admin
def is_bot_admin(chat_id: int) -> bool:
    chat = bot.get_chat(chat_id)
    return chat.type != 'admin' # Bot is considered "admin" in non-private chats

# Function to check if user is admin
def is_chat_admin(chat_id: int, user_id: int) -> bool:
    chat = bot.get_chat(chat_id)
    return chat.type == 'admin' or user_id

# Define button labels
BUTTON_WELCOME = "🌟 Welcome Settings"
BUTTON_ANTISPAM = "🛡️ Anti-Spam Settings"

# Define emojis
EMOJI_WARN = "⚠️"

# Anti-spam variables (adjust as needed)
antispam_threshold = 5  # Maximum messages allowed within the time window
antispam_time_window = 5  # Time window in seconds
antispam_action = "mute"  # "mute" or "kick"

# Dictionary to track user message timestamps
user_message_timestamps = {}

# Handle /help command
@bot.message_handler(commands=["help"])
def help_command(message: types.Message):
    help_message = """✨ **Official Arm Military Moderation Telegram Bot** ✨\n\n\
**Here are the commands you can use:**\n\n\
🤖 **Bot Commands:**\n\
    
  • 🚀 `/start` - Start the bot and get a welcome message.\n\
  • ℹ️ `/help` - Display this helpful menu.\n\n\
👮‍♀️ **Moderation Commands:**\n\

  • 🚫 `/ban` [user_id] [duration] [reason] - Ban a user.\n\
  • 🧹 `/ban` [user_id] --delete [duration] [reason] - Ban and delete messages.\n\
  • 🔇 `/mute` [user_id] [duration] [reason] - Mute a user.\n\
  • ✅ `/unban` [user_id] - Unban a user.\n\
  • 🔊 `/unmute` [user_id] - Unmute a user.\n\
  • ⚠️ `/warn` [user_id] [reason] - Issue a warning to a user.\n\
  • ⬆️ `/promote` [user_id] - Promote a user to admin.\n\
  • ⬇️ `/demote` [user_id] - Demote an admin to a regular user.\n\n\
⚙️ **Settings & Customization:**\n\

  • ⚙️ `/settings` - Access and modify bot settings.\n\n\
❓ **Need more help?** Contact the bot owner or group admins."""
    
    # Creating buttons
    keyboard = types.InlineKeyboardMarkup()
    contact_button = types.InlineKeyboardButton(text="This Bot Created For Arm Military Telegram Channel", url="https://t.me/armmilitary")
    keyboard.add(contact_button)

    bot.send_message(message.chat.id, help_message, parse_mode="Markdown", reply_markup=keyboard)


@bot.message_handler(commands=["promote"])
def promote_command(message: types.Message):
    if not is_bot_admin(message.chat.id):
        bot.reply_to(message, "❌ I need admin privileges to do that.")
        return
    if not is_chat_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ You need to be an admin to use this command.")
        return
    # Extract user information
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        try:
            user_id = int(message.text.split()[1])
        except (ValueError, IndexError):
            bot.reply_to(message, "❌ Please reply to a message or provide a user ID.")
            return
    try:
        # Promote the user
        bot.promote_chat_member(message.chat.id, user_id, can_change_info=True, can_post_messages=True, can_edit_messages=True,
                                can_delete_messages=True, can_invite_users=True, can_restrict_members=True,
                                can_pin_messages=True, can_promote_members=True)
        promote_message = f"🌟 User with ID {user_id} has been promoted to admin."
        bot.reply_to(message, promote_message)
    except Exception as e:
        logging.error(f"Error promoting user: {e}")
        bot.reply_to(message, "❌ An error occurred while trying to promote the user.")

@bot.message_handler(commands=["demote"])
def demote_command(message: types.Message):
    if not is_bot_admin(message.chat.id):
        bot.reply_to(message, "❌ I need admin privileges to do that.")
        return
    if not is_chat_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ You need to be an admin to use this command.")
        return
    # Extract user information
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        try:
            user_id = int(message.text.split()[1])
        except (ValueError, IndexError):
            bot.reply_to(message, "❌ Please reply to a message or provide a user ID.")
            return
    try:
        # Demote the user
        bot.promote_chat_member(message.chat.id, user_id, can_change_info=False, can_post_messages=True, can_edit_messages=True,
                                can_delete_messages=True, can_invite_users=False, can_restrict_members=False,
                                can_pin_messages=False, can_promote_members=False)
        demote_message = f"⬇️ User with ID {user_id} has been demoted from admin."
        bot.reply_to(message, demote_message)
    except Exception as e:
        logging.error(f"Error demoting user: {e}")
        bot.reply_to(message, "❌ An error occurred while trying to demote the user.")

# Handle /ban command
@bot.message_handler(commands=["ban"])
def ban_command(message: types.Message):
    if not is_bot_admin(message.chat.id):
        bot.reply_to(message, "❌ I need admin privileges to do that.")
        return
    if not is_chat_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ You need to be an admin to use this command.")
        return
    # Extract user information and reason
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        reason = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    else:
        try:
            user_id = int(message.text.split()[1])
            reason = message.text.split(maxsplit=2)[2] if len(message.text.split()) > 2 else None
        except (ValueError, IndexError):
            bot.reply_to(message, "❌ Please reply to a message or provide a user ID.")
            return
    # Extract duration and handle permanent bans
    duration_str = message.text.split(maxsplit=2)[2] if len(message.text.split()) > 2 else None
    try:
        if duration_str:
            duration = int(duration_str)
            until_date = datetime.now() + timedelta(minutes=duration)
            bot.ban_chat_member(message.chat.id, user_id, until_date=until_date)
            ban_message = f"🚫 User with ID {user_id} has been banned for {duration} minutes."
        else:
            bot.ban_chat_member(message.chat.id, user_id)
            ban_message = f"🚫 User with ID {user_id} has been banned permanently."
        # Delete user's messages (optional)
        delete_messages = message.text.lower().endswith("--delete")
        if delete_messages:
            try:
                bot.delete_message(message.chat.id, message.message_id)  # Delete ban command message
                # Add logic to delete past messages from the banned user (requires additional API calls)
            except Exception as e:
                logging.error(f"Error deleting messages: {e}")
        if reason:
            ban_message += f"\nReason: {reason}"
        bot.reply_to(message, ban_message)
    except Exception as e:
        logging.error(f"Error banning user: {e}")
        bot.reply_to(message, "❌ An error occurred while trying to ban the user.")

# Handle /mute command
@bot.message_handler(commands=["mute"])
def mute_command(message: types.Message):
    if not is_bot_admin(message.chat.id):
        bot.reply_to(message, "❌ I need admin privileges to do that.")
        return
    if not is_chat_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ You need to be an admin to use this command.")
        return
    # Extract user information and reason
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        reason = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    else:
        try:
            user_id = int(message.text.split()[1])
            reason = message.text.split(maxsplit=2)[2] if len(message.text.split()) > 2 else None
        except (ValueError, IndexError):
            bot.reply_to(message, "❌ Please reply to a message or provide a user ID.")
            return
    # Extract duration and handle permanent mutes
    duration_str = message.text.split(maxsplit=2)[2] if len(message.text.split()) > 2 else None
    try:
        if duration_str:
            duration = int(duration_str)
            until_date = datetime.now() + timedelta(minutes=duration)
            bot.restrict_chat_member(message.chat.id, user_id, until_date=until_date,
                                     can_send_messages=False, can_send_media_messages=False,
                                     can_send_other_messages=False, can_add_web_page_previews=False)
            mute_message = f"🔇 User with ID {user_id} has been muted for {duration} minutes."
        else:
            bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=False)
            mute_message = f"🔇 User with ID {user_id} has been muted permanently."
        if reason:
            mute_message += f"\nReason: {reason}"
        bot.reply_to(message, mute_message)
    except Exception as e:
        logging.error(f"Error muting user: {e}")
        bot.reply_to(message, "❌ An error occurred while trying to mute the user.")

# Handle /unban command
@bot.message_handler(commands=["unban"])
def unban_command(message: types.Message):
    if not is_bot_admin(message.chat.id):
        bot.reply_to(message, "❌ I need admin privileges to do that.")
        return
    if not is_chat_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ You need to be an admin to use this command.")
        return
    # Extract user information
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        try:
            user_id = int(message.text.split()[1])
        except (ValueError, IndexError):
            bot.reply_to(message, "❌ Please reply to a message or provide a user ID.")
            return
    try:
        # Unban the user
        bot.unban_chat_member(message.chat.id, user_id)
        # Optionally, send a welcome back message (customize as needed)
        welcome_back_message = f"👋 Welcome back, <a href='tg://user?id={user_id}'>user</a>! We're glad to have you back in the group."
        bot.send_message(message.chat.id, welcome_back_message, parse_mode="HTML")
        bot.reply_to(message, f"✅ User with ID {user_id} has been unbanned.")
    except Exception as e:
        logging.error(f"Error unbanning user: {e}")
        bot.reply_to(message, "❌ An error occurred while trying to unban the user.")

# Handle /unmute command
@bot.message_handler(commands=["unmute"])
def unmute_command(message: types.Message):
    if not is_bot_admin(message.chat.id):
        bot.reply_to(message, "❌ I need admin privileges to do that.")
        return
    if not is_chat_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ You need to be an admin to use this command.")
        return
    # Extract user information
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        try:
            user_id = int(message.text.split()[1])
        except (ValueError, IndexError):
            bot.reply_to(message, "❌ Please reply to a message or provide a user ID.")
            return
    try:
        # Unmute the user
        bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=True,
                                 can_send_media_messages=True, can_send_other_messages=True,
                                 can_add_web_page_previews=True)
        # Optionally, send a message informing the user they've been unmuted
        unmute_message = f"🗣️ You have been unmuted in the chat, <a href='tg://user?id={user_id}'>user</a>."
        bot.send_message(message.chat.id, unmute_message, parse_mode="HTML")
        bot.reply_to(message, f"✅ User with ID {user_id} has been unmuted.")
    except Exception as e:
        logging.error(f"Error unmuting user: {e}")
        bot.reply_to(message, "❌ An error occurred while trying to unmute the user.")

# Handle /warn command
@bot.message_handler(commands=["warn"])
def warn_command(message: types.Message):
    if not is_bot_admin(message.chat.id):
        bot.reply_to(message, "❌ I need admin privileges to do that.")
        return
    if not is_chat_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ You need to be an admin to use this command.")
        return
    # Extract user information and reason
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        reason = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    else:
        try:
            user_id = int(message.text.split()[1])
            reason = message.text.split(maxsplit=2)[2] if len(message.text.split()) > 2 else None
        except (ValueError, IndexError):
            bot.reply_to(message, "❌ Please reply to a message or provide a user ID.")
            return
    # Get user's warning count
    user_warnings = settings.setdefault(message.chat.id, {}).setdefault("user_warnings", {}).get(user_id, 0)
    try:
        # Increase warning count
        user_warnings += 1
        settings.setdefault(message.chat.id, {}).setdefault("user_warnings", {})[user_id] = user_warnings
        save_settings(settings)
        # Check if user has reached the warning limit
        if user_warnings >= 3:
            bot.ban_chat_member(message.chat.id, user_id)
            bot.reply_to(message, f"🚫 User with ID {user_id} has been banned permanently due to multiple warnings.")
        else:
            warn_message = f"{EMOJI_WARN} User with ID {user_id} has been warned. ({user_warnings}/3)"
            if reason:
                warn_message += f"\nReason: {reason}"
            bot.reply_to(message, warn_message)
    except Exception as e:
        logging.error(f"Error warning user: {e}")
        bot.reply_to(message, "❌ An error occurred while trying to warn the user.")

# Function to check if user is admin
def is_chat_admin(chat_id: int, user_id: int) -> bool:
    chat = bot.get_chat(chat_id)
    return chat.type == 'private' or user_id in [admin.user.id for admin in bot.get_chat_administrators(chat_id)]

# Anti-spam variables (adjust as needed)
antispam_threshold = 5  # Maximum messages allowed within the time window
antispam_time_window = 5  # Time window in seconds

# Dictionary to track user message timestamps
user_message_timestamps = {}

# Handle /settings command
@bot.message_handler(commands=["settings"])
def settings_command(message: types.Message):
    if not is_chat_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ You need to be an admin to use this command.")
        return

    main_menu = types.InlineKeyboardMarkup(row_width=1)
    main_menu.add(
        types.InlineKeyboardButton(BUTTON_WELCOME, callback_data="welcome_settings"),
        types.InlineKeyboardButton(BUTTON_ANTISPAM, callback_data="antispam_settings"),
        # ... Add more categories ...
    )
    bot.send_message(message.chat.id, "⚙️ **Bot Settings:**", reply_markup=main_menu)

# Handle callback queries for settings
@bot.callback_query_handler(func=lambda call: True)
def handle_settings_callback(call: types.CallbackQuery):
    global antispam_menu  # Declare as global
    chat_id = call.message.chat.id

    if call.data == "welcome_settings":
        welcome_menu = types.InlineKeyboardMarkup(row_width=1)
        welcome_menu.add(
            types.InlineKeyboardButton("✍️ Set Welcome Message", callback_data="set_welcome"),
            types.InlineKeyboardButton("👀 Preview Welcome Message", callback_data="preview_welcome"),
        )
        bot.edit_message_text(
            chat_id=chat_id, message_id=call.message.message_id, text="🌟 **Welcome Settings:**", reply_markup=welcome_menu
        )

    elif call.data == "antispam_settings":
        antispam_menu = types.InlineKeyboardMarkup(row_width=1)
        current_setting = settings.get(chat_id, {}).get("antispam_enabled", False)
        button_text = "🚫 Disable Anti-Spam" if current_setting else "✅ Enable Anti-Spam"
        antispam_menu.add(types.InlineKeyboardButton(button_text, callback_data="toggle_antispam"))
        bot.edit_message_text(
            chat_id=chat_id, message_id=call.message.message_id, text="🛡️ **Anti-Spam Settings:**", reply_markup=antispam_menu
        )

    elif call.data == "set_welcome":
        bot.send_message(chat_id, "✍️ Please enter the new welcome message:")
        bot.register_next_step_handler(call.message, set_welcome_message)

    elif call.data == "preview_welcome":
        preview_welcome(call)

    elif call.data == "toggle_antispam":
        # No need to declare as global again here
        current_setting = settings.get(chat_id, {}).get("antispam_enabled", False)
        settings[chat_id] = {"antispam_enabled": not current_setting}
        save_settings(settings)
        # Update the button text to reflect the new setting
        button_text = "🚫 Disable Anti-Spam" if not current_setting else "✅ Enable Anti-Spam"
        antispam_menu.keyboard[0][0].text = button_text
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=antispam_menu)
        bot.answer_callback_query(call.id, f"Anti-spam {'enabled' if not current_setting else 'disabled'}")

    # ... (Handle other settings options) ...

def set_welcome_message(message: types.Message):
    chat_id = message.chat.id
    settings[chat_id] = {"welcome_message": message.text}
    save_settings(settings)
    bot.send_message(chat_id, "✅ Welcome message updated!")

def preview_welcome(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    if chat_id in settings and "welcome_message" in settings[chat_id]:
        welcome_message = settings[chat_id]["welcome_message"]
        bot.send_message(chat_id, f"Preview:\n\n{welcome_message}", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "No welcome message is set yet.")

# Handle all messages
@bot.message_handler(func=lambda message: True)
def handle_message(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if anti-spam is enabled for this chat
    if settings.get(chat_id, {}).get("antispam_enabled", False):
        now = datetime.now()

        # Get the user's message timestamps or create an empty list
        timestamps = user_message_timestamps.setdefault(user_id, [])

        # Remove timestamps older than the time window
        timestamps = [ts for ts in timestamps if (now - ts).total_seconds() <= antispam_time_window]

        # Check if the user has exceeded the message threshold
        if len(timestamps) >= antispam_threshold:
            # User exceeded threshold, take action (e.g., mute, warn, delete message)
            take_antispam_action(chat_id, user_id, message)  # Pass the message object
            return  # Don't process the message further

        # Add the new message timestamp (now indented correctly)
        timestamps.append(now)
        user_message_timestamps[user_id] = timestamps

# Handle new chat members (welcome message)
@bot.message_handler(content_types=["new_chat_members"])
def handle_new_member(message: types.Message):
    chat_id = message.chat.id
    if chat_id in settings and "welcome_message" in settings[chat_id]:
        welcome_message = settings[chat_id]["welcome_message"]
        for new_member in message.new_chat_members:
            bot.send_message(chat_id, welcome_message.format(new_member=new_member.first_name), parse_mode="Markdown")

# Function to take anti-spam action (mute or kick)
def take_antispam_action(chat_id, user_id, message):  # Add message as a parameter
    if antispam_action == "mute":
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=False)
        bot.send_message(chat_id, f"🔇 User {message.from_user.first_name} has been muted for spamming.")
    elif antispam_action == "kick":
        bot.kick_chat_member(chat_id, user_id)
        bot.send_message(chat_id, f"👢 User {message.from_user.first_name} has been kicked for spamming.")

# Start the bot
if __name__ == "__main__":
    logging.info("Boty Miacav Apers")
    bot.polling()
