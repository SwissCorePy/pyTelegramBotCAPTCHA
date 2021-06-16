from datetime import datetime, timedelta

# Import TeleBot and the CaptchaManager
from telebot import TeleBot
from pyTelegramBotCAPTCHA import CaptchaManager


# Initialize the bot and the captcha_manager 
bot = TeleBot("token")
captcha_manager = CaptchaManager(bot_id=bot.get_me().id, default_language="en", default_timeout=90)


# Handler for correct solved captchas 
@captcha_manager.on_captcha_correct
def on_captcha_correct(captcha):
    bot.send_message(captcha.chat.id, f"✅ : Welcome {captcha.user.first_name}, you solved the captcha!")
    
    # unrestrict the user if chat type is not private
    if not captcha.chat.type == "private":

        # unrestrict the user
        captcha_manager.unrestrict_chat_member(bot, captcha.chat.id, captcha.user.id)

    # delete the captcha
    captcha_manager.delete_captcha(bot, captcha)


# Handler for wrong solved captchas 
@captcha_manager.on_captcha_not_correct
def on_captcha_not_correct(captcha):
    # Refresh the captcha if only one digit was incorrect and user did only one try
    if captcha.incorrect_digits == 1 and captcha.previous_tries < 2:

        # refresh captcha. 
        captcha_manager.refresh_captcha(bot, captcha, only_digits=True, add_noise=True, timeout=60)
    else:
        bot.send_message(captcha.chat.id, f"❌ : {captcha.user.first_name} failed the captcha!")
        
        # kick user if chat type is not private
        if not captcha.chat.type == "private":
            bot.kick_chat_member(captcha.chat.id, captcha.user.id, until_date=datetime.now() + timedelta(hours=2))
        
        # delete the captcha
        captcha_manager.delete_captcha(bot, captcha)


# Handler for timed out captchas 
@captcha_manager.on_captcha_timeout
def on_captcha_timeout(captcha):
    if not captcha.solved:
        bot.send_message(captcha.chat.id, f"❌ : {captcha.user.first_name} did not solve the captcha!")
        
        # kick user if chat type is not private
        if not captcha.chat.type == "private":
            bot.kick_chat_member(captcha.chat.id, captcha.user.id, until_date=datetime.now() + timedelta(hours=2))
        
        # delete the captcha
        captcha_manager.delete_captcha(bot, captcha)

# Handler for new chat members
@bot.message_handler(content_types=["new_chat_members"])
def new_member(message):
    # get new chat member
    new_user_id = message.json.get("new_chat_member").get("id")
    new_user = bot.get_chat_member(message.chat.id, new_user_id).user

    # Restrict new member
    captcha_manager.restrict_chat_member(bot, message.chat.id, new_user.id)

    # send random captcha
    captcha_manager.send_random_captcha(bot, message.chat, new_user, only_digits=True)

# Test command
@bot.message_handler(commands=["test"])
def test(message):
    if (message.chat.type == "private"):
        # send random captcha
        captcha_manager.send_random_captcha(bot, message.chat, message.from_user, only_digits=True)

# Handler for callback queries
@bot.callback_query_handler(func=lambda callback:True)
def on_callback(callback):
    # update captcha
    captcha_manager.update_captcha(bot, callback)


bot.polling()
