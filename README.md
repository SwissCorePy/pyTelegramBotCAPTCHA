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
  
## Get started:
#### Import the CapchaManager:
```python
from pyTelegramBotCAPTCHA import CaptchaManager
```
  
---
  
#### Initialize the CaptchaManager:

Its required to pass the user_id of your `TeleBot` instance! You get it with `bot.get_me().id` <br />
You can add the following optional parameters:
  * `default_language` (str) the default language to use if not set in `captcha_manager.send_random_captcha(...)`. Currently supported "en", "ru" and "de"
  * `default_timeout` (float) the default timeout to use if not set in `captcha_manager.send_random_captcha(...)`
  * `fonts` (list) the fonts to use instead of the builtin ones (must be a list of .ttf file paths). You can user as many font as you like, but keep in mind that the all the fonts are loaded into your memory, so use a lot but not to many.
  
```python
captcha_manager = CaptchaManager(bot.get_me().id, default_language="ru", default_timeout=90, fonts=["path/to/font1.ttf", "path/to/font2.ttf"])
``` 
 
---
  
#### Add a message handler for new chat members:

We restrict the new chat member and send a new captcha that he must solve. <br />
Its required to pass your `TeleBot`instance, the `Chat` object and the `User` object. <br />
You can add the following optional parameters:
  * `language` (str) to choose a language
  * `add_noise` (bool) to add noise to the image
  * `only_digits` (bool) to use only ditgits instead of hexdigits
  * `timeout` (float) to set a timeout for the captcha in seconds. if not defined in `default_timeout` nor `timeout`the user has infinit time to solve the captcha 
  
```python
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
```

---
  
#### Add a callback message handler:

Its required to pass your `TeleBot` instance the `CallbackQuery` object. <br />
The function automatically returns if `callback` was not from a CAPTCHA button. <br />
If the wrong user clicks on a button he gets an callback answer and the function returns.
  
```python
@bot.callback_query_handler(func=lambda callback:True)
def on_callback(callback: types.CallbackQuery):
  # update the captcha
  captcha_manager.update_captcha(bot, callback)
```
  
---
  
#### Add captcha handler functions:
  
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
  * `solved`(bool) has the user solved the CAPTCHA? it does not matter if he solved it correct

Lets add our first captcha handler that handles correct solved CAPTCHAs.
  
```python
@captcha_manager.on_captcha_correct
def on_correct(captcha):
  bot.send_message(captcha.chat.id, "Congrats! You solved the CAPTCHA")
  # We unrestrict the chat member because he solved the CAPTCHA correct.
  bot.restrict_chat_member(captcha.chat.id, captcha.user.id, None,
    True, True, True, True, True, True, True, True)
  captcha_manager.delete_captcha(bot, captcha)
```

Lets add a handler that handles wrong solved CAPTCHAs. We give the user a second try if only one digit was wrong and the user only tried it once. <br />
We use the attributes `incorrect_digits` and `previous_tries`.
  
```python
@captcha_manager.on_captcha_not_correct
def on_not_correct(captcha):
  if (captcha.incorrect_digits == 1 and captcha.previous_tries < 2):
    captcha_manager.refresh_captcha(bot, captcha)
  else:
    # We ban the chat member because he failed solving the CAPTCHA.
    bot.kick_chat_member(captcha.chat.id, captcha.user.id)
    bot.send_message(captcha.chat.id, f"{captcha.user.first_name} failed solvinng the CAPTCHA and was banned!")
    captcha_manager.delete_captcha(bot, captcha)
```

Now lets add a handler that handles timed out CAPTCHAs
                                                                    
```python
@captcha_manager.on_captcha_timeout
def on_timeout(captcha):
  # We ban the chat member because he did not solve the CAPTCHA.
  bot.kick_chat_member(captcha.chat.id, captcha.user.id)
  bot.send_message(captcha.chat.id, f"{captcha.user.first_name} did not solve the CAPTCHA and was banned!")
  captcha_manager.delete_captcha(bot, captcha)
```

---
Thats it! <br />
For an working example, take a look at the `captcha_bot.py` file in the 'examples' folder.
  
