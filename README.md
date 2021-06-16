# <p align="left">pyTelegramBotCAPTCHA

<p align="left">An easy to use and (hopefully useful) image CAPTCHA soltion for <a href="https://github.com/eternnoir/pyTelegramBotAPI">pyTelegramBotAPI</a>.

[![PyPi Package Version](https://img.shields.io/pypi/v/pyTelegramBotCAPTCHA.svg)](https://pypi.python.org/pypi/pyTelegramBotCAPTCHA)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pyTelegramBotAPI.svg)](https://pypi.python.org/pypi/pyTelegramBotAPI)
  
---
  
## Installation:
```
pip install pyTelegramBotCAPTCHA
```
  
*Do not forget to update the package from time to time by calling <br />
`pip install pyTelegramBotCAPTCHA --upgrade`*
  
---
  
## Description:
Do you have problems with userbots that spam your groups or add your group members to other chats? 
Then this package can help you to protect your groups and members! 
It's very easy to integrate into your existing bot and also easy to customize the CAPTCHA image with your own fonts. <br />
You can also choose between digits and hexdigits for your CAPTCHA generation. <br />
*Note: You should have basic knowledge about the pyTelegramBotAPI* <br />
![Example1](https://i.ibb.co/jWv61xr/Bildschirmfoto-2021-06-15-um-17-52-15.png "Example how it looks")
![Example2](https://i.ibb.co/vZkGgw5/Bildschirmfoto-2021-06-15-um-18-18-52.png "Example how it looks")

---
  
## Writing a CAPTCHA bot:
  
#### Import TeleBot and the CapchaManager:
```python
from telebot import TeleBot
from pyTelegramBotCAPTCHA import CaptchaManager
```
  
---
  
#### Initialize the bot and the captcha_manager:

`CaptchaManager` requires the `user_id` of your `TeleBot` instance! You get it with `bot.get_me().id` <br />
You can add the following optional parameters:
  * `default_language` (str) the default language to use if not set in `captcha_manager.send_random_captcha(...)`. Default is "en". Currently supported "en", "ru" and "de"
  * `default_timeout` (float) the default timeout to use if not set in `captcha_manager.send_random_captcha(...)`. Default is `None` but we will use a `default_timeout` of 90 seconds for our CAPTCHAs.
  * `fonts` (list) the fonts to use instead of the builtin ones (must be a list of .ttf file paths). You can choose as many fonts as you like, but keep in mind that all the fonts are loaded into your memory, so use a lot but not to many. <br />
  
```python
bot = TeleBot("TOKEN")
captcha_manager = CaptchaManager(bot.get_me().id, default_timeout=90)
``` 
*Note: Make sure to actually replace TOKEN with your own API token*
 
---
  
#### Add a message handler for new chat members:

We need a message handler to restrict the new member and sending a CAPTCHA to solve when a new user joins the group. <br />
`captcha_manager.restrict_chat_member()` requires your `TeleBot` instance, the `chat_id` and the `user_id`. It disables all permissions of a chat member.<br />
`captcha_manager.send_random_captcha()` requires your `TeleBot` instance, the `Chat` object and the `User` object. It sends a new CAPTCHA in the chat.<br />
You can add the following optional parameters:
  * `language` (str) the language to use for this CAPTCHA
  * `add_noise` (bool) add noise to the CAPTCHA image
  * `only_digits` (bool) only use ditgits instead of hexdigits for the CAPTCHA code
  * `timeout` (float) to set a timeout for the CAPTCHA in seconds.
  
```python
# Message handler for new chat members
@bot.message_handler(content_types=["new_chat_members"])
def new_member(message):
  # get the new chat member
  new_user_id = message.json.get("new_chat_member").get("id")
  new_user = bot.get_chat_member(message.chat.id, new_user_id).user

  # Restrict the new chat member
  captcha_manager.restrict_chat_member(bot, message.chat.id, new_user.id)

  # send random CAPTCHA
  captcha_manager.send_random_captcha(bot, message.chat, new_user)
```

---

#### Add a callback query handler:

We need a callback query handler, to handle the users input when he presses a CAPTCHA button. <br />
`captcha_manager.update_captcha()` requires your `TeleBot` instance and the `CallbackQuery` object as parameters. <br />
It automatically returns if `callback` was not from a CAPTCHA or from the wrong user. <br />
If the wrong user pressed a button he gets an callback query answer denying his input. <br />
If the submit button is pressed the CAPTCHA is automatically checked and your corresponding [CAPTCHA handler function](#add-captcha-handler-functions) is called. The `timeout` is also canceled if submit is pressed.
  
```python
# Callback query handler
@bot.callback_query_handler(func=lambda callback:True)
def on_callback(callback):
  # update the CAPTCHA
  captcha_manager.update_captcha(bot, callback)
```
  
---
  
#### Add CAPTCHA handler functions:
  
This works just like you know it from message handlers from the pyTelegramBotAPI.<br />
A `Captcha` object will be passed to your functions. <br />
The `Captcha` object has the following attributes:
  * `message_id` (int) the message id of the CAPTCHA message
  * `user` (User) the user that must solve the CAPTCHA
  * `chat` (Chat) the chat
  * `users_code` (str) the code entered by the user
  * `correct_code` (str) the correct code to solve the CAPTCHA
  * `language` (str) the language of the CAPTCHA text
  * `created_at` (float) the timestemp when the CAPTCHA was created
  * `previous_tries` (int) the number of tries the user made
  * `incorrect_digits` (int) the number of digits that dont match
  * `solved` (bool) has the user solved the CAPTCHA? it does not matter if he solved it correct

Lets add our first CAPTCHA handler that handles correct solved CAPTCHAs.
`captcha_manager.unrestrict_chat_member()` requires your `TeleBot` instance, the `chat_id` and the `user_id`. It removes all restictions of a chat member.<br />
`captcha_manager.delete_captcha()` requires your `TeleBot` instance and the `Captcha` object. It removes the CAPTCHA from the chat and your memory<br />
  
```python
# Handler for correct solved CAPTCHAs
@captcha_manager.on_captcha_correct
def on_correct(captcha):
  bot.send_message(captcha.chat.id, "Congrats! You solved the CAPTCHA!")
  # We unrestrict the chat member because he solved the CAPTCHA correct.
  captcha_manager.unrestrict_chat_member(bot, captcha.chat.id, captcha.user.id)
  # Delete the CAPTCHA
  captcha_manager.delete_captcha(bot, captcha)
```

Lets add a handler that handles wrong solved CAPTCHAs. <br />
We use the `Captcha` attributes `incorrect_digits` and `previous_tries` to give the user a second try if only one digit was incorrect. <br />
`captcha_manager.refresh_captcha()` requires your `TeleBot` instance and the `Captcha` object. It generates a new code image.<br />
You can add the following optional parameters:
  * `add_noise` (bool) add noise to the CAPTCHA image
  * `only_digits` (bool) only use ditgits instead of hexdigits for the CAPTCHA code
  * `timeout` (float) set new timeout because the previous is canceled. If not set it will `captcha_manager.default_timeout` (if set).
  
```python
# Handler for wrong solved CAPTCHAs
@captcha_manager.on_captcha_not_correct
def on_not_correct(captcha):
  # Check if only one dicit was incorrect and the user only did one try
  if (captcha.incorrect_digits == 1 and captcha.previous_tries < 2):
    # Refresh the CAPTCHA
    captcha_manager.refresh_captcha(bot, captcha)
  else:
    # We ban the chat member because he failed solving the CAPTCHA.
    bot.kick_chat_member(captcha.chat.id, captcha.user.id)
    bot.send_message(captcha.chat.id, f"{captcha.user.first_name} failed solving the CAPTCHA and was banned!")
    # Delete the CAPTCHA
    captcha_manager.delete_captcha(bot, captcha)
```

Now lets add a handler that handles timed out CAPTCHAs
                                                                    
```python
# Handler for timed out CAPTCHAS
@captcha_manager.on_captcha_timeout
def on_timeout(captcha):
  # We ban the chat member because he did not solve the CAPTCHA.
  bot.kick_chat_member(captcha.chat.id, captcha.user.id)
  bot.send_message(captcha.chat.id, f"{captcha.user.first_name} did not solve the CAPTCHA and was banned!")
  captcha_manager.delete_captcha(bot, captcha)
```

---
                                                                    
#### The finished CAPTCHA bot
                                                                    
Now we only have to add the line `bot.polling()`at the end of our script and we have a finished CAPTCHA bot that looks like this:

```python
from telebot import TeleBot
from pyTelegramBotCAPTCHA import CaptchaManager
                                                                    
bot = TeleBot("TOKEN")
captcha_manager = CaptchaManager(bot.get_me().id)

# Message handler for new chat members
@bot.message_handler(content_types=["new_chat_members"])
def new_member(message):
  new_user_id = message.json.get("new_chat_member").get("id")
  new_user = bot.get_chat_member(message.chat.id, new_user_id).user
  captcha_manager.restrict_chat_member(bot, message.chat.id, new_user.id)
  captcha_manager.send_random_captcha(bot, message.chat, new_user)
                                                                    
# Callback query handler
@bot.callback_query_handler(func=lambda callback:True)
def on_callback(callback):
  captcha_manager.update_captcha(bot, callback)
                                                                    
# Handler for correct solved CAPTCHAs
@captcha_manager.on_captcha_correct
def on_correct(captcha):
  bot.send_message(captcha.chat.id, "Congrats! You solved the CAPTCHA!")
  captcha_manager.unrestrict_chat_member(bot, captcha.chat.id, captcha.user.id)
  captcha_manager.delete_captcha(bot, captcha)

# Handler for wrong solved CAPTCHAs
@captcha_manager.on_captcha_not_correct
def on_not_correct(captcha):
  if (captcha.incorrect_digits == 1 and captcha.previous_tries < 2):
    captcha_manager.refresh_captcha(bot, captcha)
  else:
    bot.kick_chat_member(captcha.chat.id, captcha.user.id)
    bot.send_message(captcha.chat.id, f"{captcha.user.first_name} failed solving the CAPTCHA and was banned!")
    captcha_manager.delete_captcha(bot, captcha)
  
# Handler for timed out CAPTCHAS
@captcha_manager.on_captcha_timeout
def on_timeout(captcha):
  bot.kick_chat_member(captcha.chat.id, captcha.user.id)
  bot.send_message(captcha.chat.id, f"{captcha.user.first_name} did not solve the CAPTCHA and was banned!")
  captcha_manager.delete_captcha(bot, captcha)
  
bot.polling()
```
  
