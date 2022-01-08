from telebot import TeleBot
from pyTelegramBotCAPTCHA import CaptchaManager, CaptchaOptions, CustomLanguage

bot = TeleBot("TOKEN")

options = CaptchaOptions()
options.generator = "keyzend"  # "default", "keyzend", "multicolor"

captcha_manager = CaptchaManager(bot.get_me().id, default_options=options)

# Test command handler
@bot.message_handler(commands=["test"])
def test_captcha(message):
    captcha_manager.send_new_captcha(bot, message.chat, message.from_user)


# Callback query handler
@bot.callback_query_handler(func=lambda callback: True)
def on_callback(callback):
    captcha_manager.update_captcha(bot, callback)


# Handler for correct solved CAPTCHAs
@captcha_manager.on_captcha_correct
def on_correct(captcha):
    bot.send_message(captcha.chat.id, "✅ : Congrats! You solved the CAPTCHA!")
    captcha_manager.delete_captcha(bot, captcha)


# Handler for wrong solved CAPTCHAs
@captcha_manager.on_captcha_not_correct
def on_not_correct(captcha):
    bot.send_message(captcha.chat.id, f"❌ : You failed solving the CAPTCHA!")
    captcha_manager.delete_captcha(bot, captcha)


# Handler for timed out CAPTCHAS
@captcha_manager.on_captcha_timeout
def on_timeout(captcha):
    bot.send_message(captcha.chat.id, f"❌ : You did not solve the CAPTCHA!")
    captcha_manager.delete_captcha(bot, captcha)


bot.polling()
