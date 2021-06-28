from telebot import TeleBot
from pyTelegramBotCAPTCHA import CaptchaManager
from datetime import datetime, timedelta
                                                                    
bot = TeleBot("TOKEN")
captcha_manager = CaptchaManager(bot.get_me().id, default_timeout=90)

MAX_TRIES = 3
MAX_WRONG_DIGITS = 2

# Message handler for new chat members
@bot.message_handler(content_types=["new_chat_members"])
def new_member(message):
  new_user_id = message.json.get("new_chat_member").get("id")
  new_user = bot.get_chat_member(message.chat.id, new_user_id).user
  captcha_manager.restrict_chat_member(bot, message.chat.id, new_user.id)
  captcha_manager.send_random_captcha(bot, message.chat, new_user, timeout=60)
                                                                    
# Callback query handler
@bot.callback_query_handler(func=lambda callback:True)
def on_callback(callback):
  captcha_manager.update_captcha(bot, callback)
                                                                    
# Handler for correct solved CAPTCHAs
@captcha_manager.on_captcha_correct
def on_correct(captcha):
  bot.send_message(captcha.chat.id, "Congrats! You solved the CAPTCHA!")
  captcha_manager.unrestrict_chat_member(bot, captcha.chat.id, captcha.user.id)
  captcha_manager.delete_captcha(bot, captcha)

# Handler for wrong solved CAPTCHAs
@captcha_manager.on_captcha_not_correct
def on_not_correct(captcha):
  if (captcha.incorrect_digits <= MAX_WRONG_DIGITS and captcha.previous_tries < MAX_TRIES):
    captcha_manager.refresh_captcha(bot, captcha)
  else:
    bot.kick_chat_member(captcha.chat.id, captcha.user.id, until_date=(datetime.now() + timedelta(hours=1)))
    bot.send_message(captcha.chat.id, f"{captcha.user.first_name} failed solving the CAPTCHA and was kicked!")
    captcha_manager.delete_captcha(bot, captcha)
  
# Handler for timed out CAPTCHAS
@captcha_manager.on_captcha_timeout
def on_timeout(captcha):
  bot.kick_chat_member(captcha.chat.id, captcha.user.id, until_date=(datetime.now() + timedelta(hours=1)))
  bot.send_message(captcha.chat.id, f"{captcha.user.first_name} did not solve the CAPTCHA and was kicked!")
  captcha_manager.delete_captcha(bot, captcha)
  
bot.polling()