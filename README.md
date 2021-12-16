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
![Example1](https://i.ibb.co/fHxr7nh/Bildschirmfoto-2021-08-25-um-18-57-59.png "Example how it looks")
![Example2](https://i.ibb.co/X7mkccY/Bildschirmfoto-2021-08-25-um-18-56-37.png "Example how it looks")

---
  
## Writing a simple CAPTCHA bot:
  
#### Import TeleBot and the CapchaManager:
```python
from telebot import TeleBot
from pyTelegramBotCAPTCHA import CaptchaManager
```
  
---
  
#### Initialize the bot and the captcha_manager:

`CaptchaManager` requires the `user_id` of your `TeleBot` instance! You get it with `bot.get_me().id` <br />
You can add the following optional parameters:
  * `default_language` (str) the default language to use if `captcha.options` is not set. Default is "en". Currently supported "en", "ru" , "de", "uz" and "ar"
  * `default_timeout` (float) the default timeout to use if `captcha.options` is not set. Default is `90`
  * `fonts` (list) the fonts to use instead of the builtin ones (must be a list of .ttf file paths). You can choose as many fonts as you like, but keep in mind that all the fonts are loaded into your memory, so use a lot but not to many. <br />
  * `code_length` (int) the length of the captcha code if `captcha.options` is not set. Must be between 4 and 12.
  * `default_options` (CaptchaOptions) a option profile. (overrides all other options)
  
```python
bot = TeleBot("TOKEN")
captcha_manager = CaptchaManager(bot.get_me().id, default_timeout=90)
``` 
*Note: Make sure to actually replace TOKEN with your own API token*
 
---
  
#### Add a message handler for new chat members:

We need a message handler to restrict the new member and sending a CAPTCHA to solve when a new user joins the group. <br />
`captcha_manager.restrict_chat_member()` requires your `TeleBot` instance, the `chat_id` and the `user_id`. It disables all permissions of a chat member.<br />
`captcha_manager.send_new_captcha()` requires your `TeleBot` instance, the `Chat` object and the `User` object. It sends a new CAPTCHA in the chat.<br />
You can add the following optional parameter:
  * `options` (CaptchaOptions) a option profile. (overrides captcha_manager.options)
  
```python
# Message handler for new chat members
@bot.message_handler(content_types=["new_chat_members"])
def new_member(message):
  # get the new chat members
  for user in message.new_chat_members:

    # Restrict the new chat member
    captcha_manager.restrict_chat_member(bot, message.chat.id, user.id)

    # send random CAPTCHA
    captcha_manager.send_new_captcha(bot, message.chat, user)
```
*Note: Service messages about non-bot users joining the chat will be soon removed from large groups. We recommend using the “chat_member” update as a replacement.*
  
---

#### Add a callback query handler:

We need a callback query handler, to handle the users input when he presses a CAPTCHA button. <br />
`captcha_manager.update_captcha()` requires your `TeleBot` instance and the `CallbackQuery` object as parameters. <br />
It automatically returns if `callback` was not from a CAPTCHA or from the wrong user. <br />
If the wrong user pressed a button he gets an callback query answer denying his input. <br />
If the submit button is pressed the CAPTCHA is automatically checked and your corresponding [CAPTCHA handler function](#add-captcha-handler-functions) is called. The `timeout` is also canceled if submit is pressed (if `options.max_incorrect_to_auto_reload` is set to 0).
  
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
  * `date` (float) the timestemp when the CAPTCHA was created
  * `previous_tries` (int) the number of tries the user made
  * `incorrect_digits` (int) (deprecated) the number of digits that dont match
  * `incorrect_chars` (int) the number of chars that dont match
  * `user_reloads_left` (int) how many reloads the user has left
  * `solved` (bool) has the user solved the CAPTCHA? it does not matter if he solved it correct
  * `options` (CaptchaOptions) the options profile of this captcha (default `captcha_manager.default_options`)

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
  # Delete the CAPTCHA
  captcha_manager.delete_captcha(bot, captcha)
```

---
                                                                    
## The finished CAPTCHA bot
                                                                    
Now we only have to add the line `bot.polling()`at the end of our script and we have a finished CAPTCHA bot that looks like this:

```python
from telebot import TeleBot
from pyTelegramBotCAPTCHA import CaptchaManager
                                                                    
bot = TeleBot("TOKEN")
captcha_manager = CaptchaManager(bot.get_me().id)

# Message handler for new chat members
@bot.message_handler(content_types=["new_chat_members"])
def new_member(message):
  for new_user in message.new_chat_members:
    captcha_manager.restrict_chat_member(bot, message.chat.id, new_user.id)
    captcha_manager.send_new_captcha(bot, message.chat, new_user)
                                                                    
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

---
  
## CaptchaOptions

This class is used to manage the options of CAPTCHA's. 
It has the following properties:
  * `generator` (str) (Default: "default") The generator to use. Currently available: "default" and "keyzend".
  * `language` (str) (Default: "en") The language to use. Currently available: "en", "ru", "de", "uz" and "ar".
  * `timeout` (int or float) (Default: 90) The timeout in seconds until the CAPTCHA expires. Must be between 30 and 600.
  * `code_length` (int) (Default: 8) The target length of the random generated code. Must be between 4 and 12
  * `max_user_reloads` (int) (Default: 2) How many times should the user to be able to refresh his captcha. If set to 0, he can not.
  * `max_attempts` (int) (Default: 2) How many attempts does the user have to solve the captcha. Must be at least 1.
  * `max_incorrect_to_auto_reload` (int) (Default: 1) How many chars can be incorrect to auto reload. If set to 0 auto reload is disabled. If set to 1 or higher, the CAPTCHA reloads automatically if the user had entered less or equal incorrect chars (if an attempt is left).
  * `add_noise` (bool) (Default: True) Add noise to the picture
  * `only_digits` (bool) (Default: False) Use only digits instead of hexdigits to generate the code.
  * `custom_language` (CustomLanguage) (Default: None) Your custom language/text for the CAPTCHA. This is helpful if your language is not supported yet.
  
*Note: Some options are ignored if `options.generator` is not set to "default". 

## Usage
  
#### Set default options:
```python
from pyTelegramBotCAPTCHA import CaptchaManager, CaptchaOptions

# Set some default properties
default_options = CaptchaOptions()
default_options.generator = "keyzend" #Use keyzend generator
default_options.language = "de" #Use german language
default_options.timeout = 120 #Use a timeout of 120 seconds

#Use this options for all CAPTCHAS generated by this captcha_manager
captcha_manager = CaptchaManager(bot_id, default_options=default_options)
  
```

#### Set custom options:
This is useful to create different option profiles for specific groups 
```python
# Set custom options for this specific CAPTCHA
options_ru = CaptchaOptions()
options_ru.language = "ru" #Use german language
options_ru.timeout = 150 #Use a timeout of 150 seconds

captcha_manager.send_new_captcha(bot, chat, user, options_ru)
```
  
---
  
## CustomLanguage

This class is used to create your own custom language lext for your CAPTCHA:
  * `text` (str) The main text to use for your captcha. Example: 'Welcome, #USER!\nPlease enter the code to verify that you are a real user.'
  * `try_again` (str) The text that is displayed if the user failed the captcha and the captcha is reloaded. Example: 'Please try it again!'
  * `your_code` (str) The text that is displayed in front of the users code. Example: 'Your code: '
  * `wrong_user` (str) The text that is displayed if the wrong user tries to push a button. Example: '❌ : This is not your task!'
  * `too_short` (str) The text that is displayed if the user submits but the answer code is shorter than the correct code. Example: '❌ : The code you entered is too short!'
  
