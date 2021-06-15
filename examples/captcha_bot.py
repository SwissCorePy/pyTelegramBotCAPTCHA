# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import telebot
from telebot import types


bot = telebot.TeleBot("token")
bot_id = bot.get_me().id

# Import the CaptchaManager
from pyTelegramBotCAPTCHA import Captcha, CaptchaManager

# Initialize the CaptchaManager
#   `bot_id`: int (required) = the user_id of your bot
#
#   `default_language`: str (optional) = The language to use if not defined in 
#       `captcha_manager.send_random_captcha(...)`
#
#   `default_timeout`: float (optional) = The timeout (in seconds) to use if not defined in
#       `captcha_manager.send_random_captcha(...)`
#
#   `fonts`: list (optional) = A list of the fonts (.ttf) to use instead of the builtin ones   
captcha_manager = CaptchaManager(bot_id=bot_id, default_language="en", default_timeout=90)



# Handle correct solved captchas 
@captcha_manager.on_captcha_correct
def on_captcha_correct(captcha: Captcha):
    bot.send_message(captcha.chat.id, f"✅ : Welcome {captcha.user.first_name}, you solved the captcha!")
    
    # unrestrict the user if chat type is not private
    if not captcha.chat.type == "private":

        # unrestrict the user
        bot.restrict_chat_member(captcha.chat.id, captcha.user.id, None,
            True, True, True, True, True, True, True, True)

    # remove the captcha
    captcha_manager.delete_captcha(bot, captcha)


# Handle wrong solved captchas 
@captcha_manager.on_captcha_not_correct
def on_captcha_not_correct(captcha: Captcha):
    # Refresh the captcha if only one digit was incorrect and user did only one try
    if captcha.incorrect_digits == 1 and captcha.previous_tries < 2:

        # refresh captcha. you can use new parameters to create a harder or easyier captcha
        captcha_manager.refresh_captcha(bot, captcha, only_digits=True, add_noise=True, timeout=60)
    else:
        bot.send_message(captcha.chat.id, f"❌ : {captcha.user.first_name} failed the captcha!")
        
        # kick user if chat type is not private
        if not captcha.chat.type == "private":
            bot.kick_chat_member(captcha.chat.id, captcha.user.id, until_date=datetime.now() + timedelta(hours=2))
        
        # remove the captcha
        captcha_manager.delete_captcha(bot, captcha)


# Handle timed out captchas 
@captcha_manager.on_captcha_timeout
def on_captcha_timeout(captcha: Captcha):
    if not captcha.solved:
        bot.send_message(captcha.chat.id, f"❌ : {captcha.user.first_name} did not solve the captcha!")
        
        # kick user if chat type is not private
        if not captcha.chat.type == "private":
            bot.kick_chat_member(captcha.chat.id, captcha.user.id, until_date=datetime.now() + timedelta(hours=2))
        
        # remove the captcha
        captcha_manager.delete_captcha(bot, captcha)


@bot.message_handler(content_types=["new_chat_members"])
def new_member(message: types.Message):
    # get new chat member
    new_user_id = message.json.get("new_chat_member").get("id")
    new_user = bot.get_chat_member(message.chat.id, new_user_id).user

    # Restrict new member
    bot.restrict_chat_member(message.chat.id, new_user.id, None,
        False, False, False, False, False, False, False, False)

    # send random captcha
    captcha_manager.send_random_captcha(bot, message.chat, new_user, only_digits=True)


@bot.message_handler(commands=["test"])
def test(message: types.Message):
    if (message.chat.type == "private"):
        # send random captcha
        captcha_manager.send_random_captcha(bot, message.chat, message.from_user, only_digits=True)


@bot.callback_query_handler(func=lambda callback:True)
def on_callback(callback: types.CallbackQuery):
    # update captcha (returns if wrong user or not a captcha callback)
    captcha_manager.update_captcha(bot, callback)


bot.polling()
