# <p align="left">pyTelegramBotCAPTCHA

<p align="left">An easy to use and (hopefully useful) image CAPTCHA soltion for <a href="https://github.com/eternnoir/pyTelegramBotAPI">pyTelegramBotAPI</a>.

[![PyPi Package Version](https://img.shields.io/pypi/v/pyTelegramBotCAPTCHA.svg)](https://pypi.python.org/pypi/pyTelegramBotCAPTCHA)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pyTelegramBotAPI.svg)](https://pypi.python.org/pypi/pyTelegramBotAPI)

  
![Example](https://i.ibb.co/jWv61xr/Bildschirmfoto-2021-06-15-um-17-52-15.png "Example how it looks")
  
### Installation:
```
pip install pyTelegramBotCAPTCHA
```
  
*Do not forget to update the package from time to time by calling 
  `pip install pyTelegramBotCAPTCHA --upgrade`*

  
### Description:
Do you have problems with userbots that spam your groups or add your group members to other chats? 
Then this package can help you to protect your groups and members! 
It's very easy to integrate into your existing bot and also easy to customize the CAPTCHA image with your own fonts.

### Get started:
*Import the CapchaManager*
```
from pyTelegramBotCAPTCHA CaptchaManager
```
*Initialize the CaptchaManager*

Its required to pass the user_id of your bot! `bot.get_me().id`
You can add the optional parameters `default_language`, `default_timeout` and `fonts`.
```
captcha_manager = CaptchaManager(`bot.get_me().id`, default_language="ru", default_timeout=90, fonts=["path/font1.ttf", "path/font2.ttf"])
``` 
*Add chapcha handler functions:*
  
This functions are executed if the decorator event is triggered. just like you know it from pyTelegramBotAPI.
A `captcha` object will be passed to your functions. it includes the `message_id` of the captcha, the `chat` and `user` object
and some more propperties to do what ever you need.
```
@capcha_manager.on_captcha_correct
def on_correct(captcha):
  #the code that must be executed if a user solves a captcha

@chaptcha_manager.on_chatcha_not_correct
def on_not_correct(captcha):
  #the code that must be executed if a user solves a captcha wrong
  
@chaptcha_manager.on_captcha_timeout
def on_timeout(captcha):
  #the code that must be executed if a user has not solves his captcha after 'timeout' seconds
```

I will update and complete the README file soon ;) 
For an working example, take a look at the `captcha_bot.py` file in the 'examples' folder
  
