# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from threading import Thread, Timer

import telebot
from telebot import types

from pyTelegramBotCAPTCHA import Captcha, CaptchaManager

bot = telebot.TeleBot("token")
captcha_manager = CaptchaManager(default_language="en", default_timeout=90)


def try_delete_message(chat_id, message_id):
    try: bot.delete_message(chat_id, message_id)
    except: pass

def send_temp_message(chat_id, text, parse_mode=None, display_time=15):
    m = bot.send_message(chat_id, text, parse_mode=parse_mode)
    Timer(interval=display_time, function=try_delete_message, args=[m.chat.id, m.message_id])


@captcha_manager.on_captcha_correct
def on_captcha_correct(captcha: Captcha):
    bot.send_message(captcha.chat.id, f"✅ : Welcome {captcha.user.first_name}, you solved the captcha!")
    if not captcha.chat.type == "private":
        bot.restrict_chat_member(captcha.chat.id, captcha.user.id, None,
            True, True, True, True, True, True, True, True)
    captcha_manager.delete_captcha(bot, captcha)


@captcha_manager.on_captcha_not_correct
def on_captcha_not_correct(captcha: Captcha):
    if captcha.incorrect_digits == 1 and captcha.previous_tries < 2:
        captcha_manager.refresh_captcha(bot, captcha, only_digits=True, add_noise=True, timeout=60)
    else:
        send_temp_message(captcha.chat.id, f"❌ : {captcha.user.first_name} failed the captcha!")
        if not captcha.chat.type == "private":
            bot.kick_chat_member(captcha.chat.id, captcha.user.id, until_date=datetime.now() + timedelta(hours=2))
        captcha_manager.delete_captcha(bot, captcha)


@captcha_manager.on_captcha_timeout
def on_captcha_timeout(captcha: Captcha):
    if not captcha.solved:
        send_temp_message(captcha.chat.id, f"❌ : {captcha.user.first_name} did not solve the captcha!")
        if not captcha.chat.type == "private":
            bot.kick_chat_member(captcha.chat.id, captcha.user.id, until_date=datetime.now() + timedelta(hours=2))
        captcha_manager.delete_captcha(bot, captcha)


@bot.message_handler(content_types=["new_chat_members"])
def new_member(message: types.Message):
    new_user_id = message.json.get("new_chat_member").get("id")
    new_user = bot.get_chat_member(message.chat.id, new_user_id).user
    bot.restrict_chat_member(message.chat.id, new_user.id, None,
        False, False, False, False, False, False, False, False)
    captcha_manager.send_random_captcha(bot, message.chat, new_user, only_digits=True)


@bot.message_handler(commands=["test"])
def test(message: types.Message):
    if (message.chat.type == "private"):
        captcha_manager.send_random_captcha(bot, message.chat, message.from_user, only_digits=True)
    try_delete_message(message.chat.id, message.message_id)


@bot.callback_query_handler(func=lambda callback:True)
def on_callback(callback: types.CallbackQuery):
    captcha_manager.update_captcha(bot, callback)


bot.polling()
