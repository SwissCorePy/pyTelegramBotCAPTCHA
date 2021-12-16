# -*- coding: utf-8 -*-
import os
import random
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Tuple, List, Optional, Union
from threading import Timer
import requests

try:
    import ujson as json
except:
    import json

from captcha.image import ImageCaptcha
from PIL import Image
from telebot import TeleBot, types


_base_path = Path(__file__).parent.absolute()
_fonts_path = _base_path / "data" / "fonts"
_captcha_saves = (Path(".") / ".captcha-saves").parent.absolute()
_fonts = []
_generators = ["default", "keyzend"]

MIN_TIMEOUT = 30
MAX_TIMEOUT = 600
MIN_CODE_LENGTH = 4
MAX_CODE_LENGTH = 12


digits = "1234567890"
hexdigits = digits + "ABCDEF"

languages: Dict = None 
with (_base_path / "data" / "languages.json").open("r",encoding='utf-8') as f:
    languages = json.loads(f.read())


class MissingHandler(Exception):
    def __init__(self, error_info=None):
        super().__init__(self)
        self.error_info = error_info or "No Handler declared!"
    
    def __str__(self):
        return self.error_info


class CustomLanguage:
    def __init__(self, base_language: str="en", text: Optional[str]=None, try_again: Optional[str]=None,
            your_code: Optional[str]=None, wrong_user: Optional[str]=None, too_short: Optional[str]=None) -> None:
        """
        Use this class to customize the texts of a captcha
        :param base_language: The base language to use
        :param text: The main text to use for your captcha.
            Example: 'Welcome, #USER!\nPlease enter the code to verify that you are a real user.'
            NOTE: `#USER` is gonna be replaced by the user's first_name
        :param try_again: The text that is displayed if the user failed the captcha and the captcha is reloaded.
            Example: 'Please try it again!'
        :param your_code: The text that is displayed in front of the users code.
            Example: 'Your code: '
            Keep in mind that the user's input will be added to the end of this text. 
        :param wrong_user: The text that is displayed if the wrong user tries to push a button.
            Example: '❌ : This is not your task!'
            This text is only displayed to the user who has pressed a button
        :param too_short: The text that is displayed if the user submits but the answer code is shorter than the correct code
            Example: '❌ : The code you entered is too short!'
        """
        if not base_language in languages.keys():
            raise NotImplementedError
        self._text = text or languages[base_language]["text"]
        self._try_again = try_again or languages[base_language]["try_again"]
        self._your_code = your_code or languages[base_language]["your_code"]
        self._wrong_user = wrong_user or languages[base_language]["wrong_user"]
        self._too_short = too_short or languages[base_language]["too_short"]
    
    def to_dict(self):
        return {
            "text": self.text, "try_again": self.try_again, "your_code": self.your_code, 
            "wrong_user": self.wrong_user, "too_short": self.too_short
        }

    @property
    def text(self) -> str: return self._text
    @property
    def try_again(self) -> str: return self._try_again
    @property
    def your_code(self) -> str: return self._your_code
    @property
    def wrong_user(self) -> str: return self._wrong_user
    @property
    def too_short(self) -> str: return self._too_short

    @text.setter
    def text(self, your_text: str):
        """
        The main text to use for your captcha.
        Example: 'Welcome, #USER!\nPlease enter the code to verify that you are a real user.'
        NOTE: `#USER` is gonna be replaced by the user's first_name
        """
        if not isinstance(your_text, str): raise TypeError("Must be str")
        elif your_text == "": raise ValueError("This Text cannot be empty!")
        self._text = your_text + (" " if not your_text.endswith(" ") else "")
    
    @try_again.setter
    def try_again(self, your_text: str):
        """
        The text that is displayed if the user failed the captcha and the captcha is reloaded.
        Example: 'Please try it again!'
        """
        if not isinstance(your_text, str): raise TypeError("Must be str")
        elif your_text == "": raise ValueError("This Text cannot be empty!")
        self._try_again = your_text + (" " if not your_text.endswith(" ") else "")
    
    @your_code.setter
    def your_code(self, your_text: str):
        """
        The text that is displayed in front of the users code.
        Example: 'Your code: '
        Keep in mind that the user's input will be added to the end of this text. 
        """
        if not isinstance(your_text, str): raise TypeError("Must be str")
        elif your_text == "": raise ValueError("This Text cannot be empty!")
        self._your_code = your_text + (" " if not your_text.endswith(" ") else "")
    
    @wrong_user.setter
    def wrong_user(self, your_text: str):
        """
        The text that is displayed if the wrong user tries to push a button.
        Example: '❌ : This is not your task!'
        This text is only displayed to the user who has pressed a button
        """
        if not isinstance(your_text, str): raise TypeError("Must be str")
        elif your_text == "": raise ValueError("This Text cannot be empty!")
        self._wrong_user = your_text
    
    @too_short.setter
    def too_short(self, your_text: str):
        """
        The text that is displayed if the user submits but the answer code is shorter than the correct code
        Example: '❌ : The code you entered is too short!'
        """
        if not isinstance(your_text, str): raise TypeError("Must be str")
        elif your_text == "": raise ValueError("This Text cannot be empty!")
        self._too_short = your_text


class CaptchaOptions:
    def __init__(self, generator: str="default", language: str="en", timeout: Union[int,float]=90, 
            code_length: int=8, max_user_reloads: int=2, max_attempts: int=2, 
            max_incorrect_to_auto_reload: int=2, add_noise: bool=True, only_digits: bool=False,
            custom_language: Optional[CustomLanguage]=None) -> None:
        """
        Use this class to create a captcha options profile.
        :param generator: The generator to use. Currently available: `"default"` and `"keyzend"`
        :param language: The language to use
        :param timeout: The timeout to use. (min: 30, max: 600)
        :param code_length: The length of the code (min: 4, max: 12)
        :param max_user_reloads: How many times can the user refresh his captcha. 0 or lower means he can not.
        :param max_attempts: How many attempts does the user have to solve the captcha. (min: 1)
        :param max_incorrect_to_auto_reload: How many chars can be incorrect to auto reload. 
            if <= 0: on_not_correct event is triggered
            if >1: if n chars are incorrect the captcha is reloaded automatically (if an attempt is left)
        :param add_noise: Add noise to the image
        :param only_digits: Use only digits instead of hexdigits.
        :param custom_language: A custom language to use (overrides `language`)

        NOTE: If `generator` is not set to `"default"`, some options will be ignored/overwritten 
        """
        if not generator.lower() in _generators: raise ValueError("This generator seems not to exist")
        if not language.lower() in languages and not custom_language: raise NotImplementedError("This language is not suported yet")
        if not MIN_TIMEOUT <= timeout <= MAX_TIMEOUT: raise ValueError("timeout must be between 30 and 600 (in seconds)")
        if not MIN_CODE_LENGTH <= code_length <= MAX_CODE_LENGTH: raise ValueError("code_lenght must be between 4 and 12")
        if max_attempts < 1: raise ValueError("max_attempts must be at least 1")

        self._generator: str = generator.lower()
        self._language: str = language.lower() if not custom_language else "custom"
        self._timeout: float = timeout
        self._code_length: int = code_length
        self._max_user_reloads: int = max_user_reloads
        self._max_attempts: int = max_attempts
        self._max_incorrect_to_auto_reload: int = max_incorrect_to_auto_reload
        self._add_noise: bool = add_noise
        self._only_digits: bool = only_digits
        self.custom_language: CustomLanguage = custom_language

    @property
    def generator(self) -> str: return self._generator
    @property
    def language(self) -> str: return self._language
    @property
    def timeout(self) -> Union[float, int]: return self._timeout
    @property
    def max_user_reloads(self) -> int: return self._max_user_reloads
    @property
    def max_attempts(self) -> int: return self._max_attempts
    @property
    def max_incorrect_to_auto_reload(self) -> int: return self._max_incorrect_to_auto_reload
    @property
    def custom_language(self): return self._custom_language

    @property
    def code_length(self) -> int:
        if self.generator == "keyzend": 
            return 5
        return self._code_length

    @property
    def add_noise(self) -> bool: 
        if self.generator == "keyzend": 
            return False
        return self._add_noise
    
    @property
    def only_digits(self) -> bool: 
        if self.generator == "keyzend": 
            return True
        return self._only_digits
    

    @generator.setter
    def generator(self, value: str):
        """
        The generator to use. Currently available: `"default"` and `"keyzend"`
        Default: "default"
        NOTE: If not set to "default", some options will be ignored 
        """
        value = value.lower()
        if not value in _generators:
            self._generator = "default"
            raise ValueError("This generator seems not to exist")
        self._generator = value
    
    @language.setter
    def language(self, value: str):
        """
        The language to use
        Default: "en"
        """
        if not value.lower() in languages.keys(): 
            raise NotImplementedError("This language is not implemented now. Please use another language create your own language profile using `CustomLanguage`.")
        self._language = value.lower()

    @timeout.setter
    def timeout(self, value: Union[int, float]):
        """
        The timeout to use. (in seconds) Must be at least 30 and maximum 600 seconds
        Default: 90
        """
        if not (isinstance(value, int) or isinstance(value, float)): 
            raise TypeError("timeout must be a int or float")
        elif not MIN_TIMEOUT <= value <= MAX_TIMEOUT: 
            raise ValueError("timeout must be between 30 and 600")
        self._timeout = value

    @code_length.setter
    def code_length(self, value: int):
        """
        The length of the generated code (min: 4, max: 12)
        Default: 8
        """
        if not isinstance(value, int):
            raise TypeError("Must be int")
        elif not MIN_CODE_LENGTH <= value <= MAX_CODE_LENGTH:
            self._code_length = value
            raise ValueError("Must be between 4 and 12")

    @max_user_reloads.setter
    def max_user_reloads(self, value: int):
        """
        How many times can the user refresh his captcha. 0 or lower means he can not.
        Default: 2
        """
        self._max_user_reloads = value
    
    @max_attempts.setter
    def max_attempts(self, value: int):
        """
        How many attempts does the user have to solve the captcha. 
        Must be at least 1
        Default: 2
        """
        if value < 1:
            raise ValueError("Must be at least 1")
        self._max_attempts = value
    
    @max_incorrect_to_auto_reload.setter
    def max_incorrect_to_auto_reload(self, value: int):
        """
        How many chars can be incorrect to auto reload. 
        if <= 0: on_not_correct event is triggered
        if 1 or higher -> if one char is incorrect the captcha is reloaded automatically (if an attempt is left)
        Default: 1
        """
        self._max_incorrect_to_auto_reload = value

    @add_noise.setter
    def add_noise(self, value: bool):
        """
        Default: True
        Add noise to the captcha image
        """
        self._add_noise = bool(value)

    @only_digits.setter
    def only_digits(self, value: bool):
        """
        Use only digits instead of hexdigits to generate the captcha image
        Default: False
        """
        self._only_digits = bool(value)

    @custom_language.setter
    def custom_language(self, value: CustomLanguage):
        """
        A custom Language to use.
        You can setup your own language if yours is not implemented
        Default: None
        """
        if value:
            if not isinstance(value, CustomLanguage):
                raise TypeError("must be a CustomLanguage type")
            self._custom_language = value
            self._language = "custom"
            languages["custom"] = value.to_dict()


class Captcha(types.JsonDeserializable, types.JsonSerializable):
    @classmethod
    def de_json(cls, json_str):
        if not json_str: return None
        obj = json.loads(json_str)
        if not "options" in obj.keys():
            pass #TODO: Expire
        if not obj["options"]:
            obj["options"] = CaptchaManager._instance.default_options
        else:
            opt = CaptchaOptions()
            opt._generator = obj["options"]["generator"]
            opt._language = obj["options"]["language"]
            opt._timeout = obj["options"]["timeout"]
            opt._code_length = obj["options"]["code_length"]
            opt._max_user_reloads = obj["options"]["max_user_reloads"]
            opt._max_attempts = obj["options"]["max_attempts"]
            opt._max_incorrect_to_auto_reload = obj["options"]["max_incorrect_to_auto_reload"]
            opt._add_noise = obj["options"]["add_noise"]
            opt._only_digits = obj["options"]["only_digits"]
            obj["options"] = opt
        obj['chat'] = types.Chat(**obj['chat'])
        obj['user'] = types.User(**obj['user'])
        return cls(bot=None, **obj)

    def __init__(self, bot: TeleBot, chat: types.Chat, user: types.User, options: CaptchaOptions, **kwargs) -> None:
        self.solved = False
        self.chat = chat
        self.user = user
        self._custom_options = options is not None
        self.options = options or CaptchaManager._instance.default_options

        self._timeout_thread = None

        if not bot:
            # Loaded from file
            self._captcha_id = kwargs["captcha_id"]

            self.previous_tries = kwargs["previous_tries"]
            self.correct_code = kwargs["correct_code"]
            self.users_code = kwargs["users_code"]
            self.message_id = kwargs["message_id"]
            self.date = kwargs["date"]
            self.user_reloads_left = kwargs["user_reloads_left"]
        
            self.image = None
            self.reply_markup = None
            
        else:
            self._captcha_id = f"{CaptchaManager._bot_id}={chat.id}={user.id}"
            
            self.previous_tries = 0
            self.users_code = ""
            self.user_reloads_left = self.options.max_user_reloads

            self.correct_code, self.image = _random_codeimage(self.options)

            text = languages[self.options.language]["text"].replace("#USER", _user_link(self.user)) + "\n"
            text += languages[self.options.language]["your_code"]

            m = self.message_id = bot.send_photo(
                chat_id=self.chat.id, 
                photo=self.image,
                caption=text,
                reply_markup=_code_input_markup(self),
                parse_mode="HTML"
            )
            self.message_id = m.message_id
            self.date = m.date
            self._save_file()

        
    @property
    def incorrect_digits(self) -> int:
        """
        This property is deprecated! use `incorrect_chars` instead!
        """
        return self.incorrect_chars
        

    @property
    def incorrect_chars(self) -> int:
        """
        How many chars do not match?
        """
        users_code = self.users_code.ljust(self.options.code_length, " ")
        count = 0
        for i, d in enumerate(users_code):
            if self.correct_code[i] != d: count += 1
        return count


    def to_json(self):
        chat_dict = {
            "id": self.chat.id,
            "type": self.chat.type,
            "title": self.chat.title,
            "username": self.chat.username
        }

        opt = None if not self._custom_options else {
            "generator": self.options.generator,
            "language": self.options.language,
            "timeout": self.options.timeout,
            "code_length": self.options.code_length,
            "max_user_reloads": self.options.max_user_reloads,
            "max_attempts": self.options.max_attempts,
            "max_incorrect_to_auto_reload": self.options.max_incorrect_to_auto_reload,
            "add_noise": self.options.add_noise,
            "only_digits": self.options.only_digits
        }

        json_dict = {
            "chat": chat_dict,
            "user": types.User.to_dict(self.user),
            "users_code": self.users_code,
            "correct_code": self.correct_code,
            "message_id": self.message_id,
            "date": self.date,
            "captcha_id": self._captcha_id,
            "previous_tries": self.previous_tries,
            "user_reloads_left": self.user_reloads_left,
            "options": opt
        }
        return json.dumps(json_dict)

    def _continue_timeout(self):
        now = datetime.now().timestamp()
        exec_at = self.date + self.options.timeout
        if now >= exec_at:
            self._timeout_thread = Timer(interval=1, 
                function=CaptchaManager._handlers["on_timeout"], args=[self])
        else:
            self._timeout_thread = Timer(interval=exec_at-now, 
                function=CaptchaManager._handlers["on_timeout"], args=[self])
        self._timeout_thread.start()

    def _reset(self, bot: TeleBot) -> None:
        new_code, new_image = _random_codeimage(self.options)
        self.date = datetime.now().timestamp()
        self.image = new_image
        self.correct_code = new_code
        self.users_code = ""
        text = languages[self.options.language]["text"].replace("#USER", _user_link(self.user)) + "\n"
        if self.previous_tries > 0:
            text += languages[self.options.language]["try_again"] + "\n"
        text += languages[self.options.language]["your_code"]
        
        self.reply_markup = _code_input_markup(self)

        bot.edit_message_media(
            types.InputMediaPhoto(self.image, text, "HTML"), 
            self.chat.id, self.message_id, reply_markup=self.reply_markup
        )

        self._save_file()
        
    def _save_file(self):
        if not os.path.exists(str(_captcha_saves)):
            os.mkdir(_captcha_saves)
        filename = self._captcha_id + ".json"
        filepath = _captcha_saves / filename
        with open(filepath, "w+",encoding="utf8") as f:
            f.write(self.to_json())
    
    def _delete_file(self):
        filename = self._captcha_id + ".json"
        filepath = _captcha_saves / filename
        if filepath.exists():
            filepath.unlink()

    def _update(self, bot: TeleBot, callback: types.CallbackQuery):
        btn = callback.data.split("=")[2]
        if (btn == "BACK"):
            self.users_code = self.users_code[:-1]
        else:
            self.users_code = (self.users_code + btn)[:self.options.code_length]

        text = languages[self.options.language]["text"].replace("#USER", _user_link(self.user)) + "\n"
        if self.previous_tries > 0:
            text += languages[self.options.language]["try_again"] + "\n"
        text += (languages[self.options.language]["your_code"] + f"<pre>{self.users_code}</pre>")

        try:
            bot.edit_message_caption(
                caption=text,
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=callback.message.reply_markup,
                parse_mode="HTML"
            )
            self._save_file()
        except: pass


class CaptchaManager:
    _handlers = {"on_correct": None, "on_not_correct": None, "on_timeout": None}
    _bot_id = None
    _instance = None

    def __init__(self, bot_id: int, default_language: str="en", default_timeout: float=MAX_TIMEOUT, fonts: List=None, 
            code_length: int=8, default_options: CaptchaOptions=None) -> None:
        """
        The Captcha Manager

        fonts=['/path/to/A.ttf', '/path/to/B.ttf']
        You can put as many fonts as you like. But be aware of your memory, all of
        the fonts are loaded into your memory, so keep them a lot, but not too
        many.

        :param bot_id: the user_id of your bot `bot.get_me().id`
        :param default_language: language to be used if not defined in `send_random_captcha`
        :param default_timeout: timeout to be used if not defined in `send_random_captcha`
        :param fonts: fonts to be used to generate CAPTCHA images. (.ttf)
        :param code_length: the lenght of the code. must be between 4-12 chars
        :param default_options: options profile to use if not defined in `send_random_captcha`.
            Overrides all other settings (except fonts)!
        """
        if self.__class__._instance:
            raise ValueError("Only one instance of CaptchaManager can exist.")
        self.__class__._instance = self
        self.__class__._bot_id = bot_id

        if not default_options:
            self.default_options: CaptchaOptions = CaptchaOptions()
            self.default_options.language = default_language
            self.default_options.timeout = default_timeout
            self.default_options.code_length = code_length
        else:
            self.default_options = default_options
        
        global _fonts
        _fonts = fonts or _fonts
        if not _fonts:
            for f in os.listdir(_fonts_path):
                if f.endswith(".ttf") and not f.startswith("."):
                    _fonts.append(str(_fonts_path / f))

        self.captchas: Dict[str, Captcha] = {}
        if os.path.exists(_captcha_saves):
            saved_captchas = os.listdir(_captcha_saves)
            for f in saved_captchas:
                if f.startswith(f"{self._bot_id}=") and f.endswith(".json"):
                    filepath = _captcha_saves / f
                    with filepath.open("r") as f:
                        json_str = f.read()
                        captcha = Captcha.de_json(json_str)
                        self.captchas[captcha._captcha_id] = captcha

    def send_new_captcha(self, bot: TeleBot, chat: types.Chat, user: types.User, options: CaptchaOptions=None):
        """
        sends a randomly generated captcha into your chat.
        :param bot: your TeleBot instance
        :param chat: the chat (chat not chat_id)
        :param user: the user who must solve the captcha (user not user_id)
        :param options: options profile to use
        :return: the generated Captcha object
        """

        if not self._handlers["on_correct"]: raise MissingHandler("No event handler declared for `on_correct`.")
        if not self._handlers["on_not_correct"]: raise MissingHandler("No event handler declared for `on_not_correct`.")
        if not self._handlers["on_timeout"]: raise MissingHandler("No event handler declared for `on_timeout`.")

        captcha = Captcha(bot, chat, user, options)
        
        if captcha._captcha_id in self.captchas.keys():
            old_captcha: Captcha = self.captchas.pop(captcha._captcha_id)
            if (old_captcha._timeout_thread):
                old_captcha._timeout_thread.cancel()
            self.delete_captcha(bot, old_captcha)
        
        captcha._timeout_thread = Timer(interval=captcha.options.timeout, function=self._handlers["on_timeout"], args=[captcha])
        captcha._timeout_thread.start()
        captcha._save_file()
        
            
        self.captchas[captcha._captcha_id] = captcha
        return captcha
        

    def send_random_captcha(self, bot: TeleBot, chat: types.Chat, user: types.User, language: str=None, 
            only_digits: bool=False, add_noise: bool=True, timeout: float=None, max_user_reloads: int=3, 
            allow_user_reloads: bool=True, code_length: int=8) -> Captcha:
        """
        This function is deprecated and will maybe removed in a future release! 
        Use `send_new_captcha()` instead!

        sends a randomly generated captcha into your chat.
        :param bot: your TeleBot instance
        :param chat: the chat (chat not chat_id)
        :param user: the user who must solve the captcha (user not user_id)
        :param language: the language to use for the captcha
        :param only_digits: using only digits or hexdigits
        :param add_noise: add noise to the image
        :param timeout: timeout must be at least 30 and maximum 600 seconds or `None`
        :param max_user_reloads: max reloads a user can make. must be at least 1
        :param options: options profile to use (overrides all other settings)
        :return: the generated Captcha object
        """

        options = CaptchaOptions()
        options.language = language or self.default_options.language
        options.only_digits = only_digits
        options.add_noise = add_noise
        options.timeout = timeout or self.default_options.timeout
        options.max_user_reloads = max_user_reloads
        options.code_length = code_length

        self.send_new_captcha(bot, chat, user, options)


        

    def restrict_chat_member(self, bot: TeleBot, chat_id: int, user_id: int) -> bool:
        """
        Set all permissions of a chat member to `False`.
        :param bot: your TeleBot instance
        :param chat_id: the Chat ID
        :param user_id: the User ID
        :retrun: True on sucess
        """
        return bot.restrict_chat_member(chat_id, user_id,
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False)
    
    def unrestrict_chat_member(self, bot: TeleBot, chat_id: int, user_id: int):
        """
        Set all permissions of a chat member to `True` which removes the restriction.
        :param bot: your TeleBot instance
        :param chat_id: the Chat ID
        :param user_id: the User ID
        :retrun: True on sucess
        """
        return bot.restrict_chat_member(chat_id, user_id,
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True)

    def update_captcha(self, bot: TeleBot, callback: types.CallbackQuery) -> None:
        """
        updates the captcha if a user has pressed a button. if submit is pressed the captcha gets checked
        :param bot: your TeleBot instance
        :param callback: the CallbackQuery
        """
        if not callback.data.startswith("?cap="): return

        user_id, btn = int(callback.data.split("=")[1]), callback.data.split("=")[2]
        captcha_id = f"{self.__class__._bot_id}={callback.message.chat.id}={user_id}"
        captcha: Captcha = self.captchas[captcha_id]

        if captcha.user.id != callback.from_user.id:
            bot.answer_callback_query(callback.id, text=languages[captcha.options.language]["wrong_user"])
            return
        if btn == "OK":
            if len(captcha.users_code) < captcha.options.code_length:
                bot.answer_callback_query(callback.id,text=languages[captcha.options.language]["too_short"], show_alert=True)
            else:
                user_id = int(callback.data.split("=")[1])
                captcha_id = f"{self.__class__._bot_id}={callback.message.chat.id}={user_id}"
                if (captcha_id in self.captchas):
                    self._check_captcha(self.captchas[captcha_id], bot)
        elif btn == 'RELOAD':
            if captcha.user_reloads_left > 0:
                captcha.user_reloads_left -= 1
                self.refresh_captcha(bot, captcha)
            else:
                bot.answer_callback_query(callback.id,languages[captcha.language]['maxreloadlimit'])
                
        else:
            captcha._update(bot, callback)
        
        bot.answer_callback_query(callback.id)

    def reset_captcha(self, bot: TeleBot, captcha: Captcha) -> None:
        """
        Resets a Captcha
        Generates new image, new code and resets the timeout. 
        :param bot:
        :param captcha:
        """
        if captcha._timeout_thread:
            captcha._timeout_thread.cancel()
            captcha._timeout_thread = None
        captcha._reset(bot)
        if captcha._timeout_thread is None:
            captcha._timeout_thread = Timer(interval=captcha.options.timeout, 
                function=self._handlers["on_timeout"], args=[captcha])
            captcha._timeout_thread.start()
    
    def refresh_captcha(self, bot: TeleBot, captcha: Captcha, 
            only_digits: Optional[bool]=None, add_noise: Optional[bool]=None, timeout: Optional[float]=None) -> None:
        """
        This function is deprecated and may be removed in a future release! 
        Use `reset_captcha(...)` instead!

        Note: This function still works, but the parameters `only_digits`, `add_noise` and `timeout` are ignored!
        """
        self.reset_captcha(bot, captcha)

    def delete_captcha(self, bot: TeleBot, captcha: Captcha) -> None:
        #self.captchas.pop(captcha._captcha_id)
        captcha._delete_file()
        try: bot.delete_message(captcha.chat.id, captcha.message_id)
        except: pass
        del captcha

    def on_captcha_correct(self, function):
        """
        Captcha correct decorator.
        This decorator can be used to decorate functions that must handle correct solved Captchas.

        Example:

        captcha_manager = CaptchaManager()

        # Handles correct solved Captchas
        @captcha_manager.captcha_correct
        def on_captcha_correct(captcha):
            bot.send_message(captcha.chat.id, captcha.user.first_name + ' solved the Captcha!')
        
        """
        def wrapper(*args, **kwargs):
            rv = function(*args, **kwargs)
            return rv
        self.__class__._handlers["on_correct"] = wrapper
        return wrapper
    
    def on_captcha_not_correct(self, function):
        """
        Captcha not correct decorator.
        This decorator can be used to decorate functions that must handle wrong solved Captchas.

        Example:

        captcha_manager = CaptchaManager()

        # Handles wrong solved Captchas
        @captcha_manager.captcha_not_correct
        def on_captcha_not_correct(captcha):
            bot.send_message(captcha.chat.id, captcha.user.first_name + ' failed the Captcha!')
        
        """
        def wrapper(*args, **kwargs):
            rv = function(*args, **kwargs)
            return rv
        self.__class__._handlers["on_not_correct"] = wrapper
        return wrapper

    def on_captcha_timeout(self, function):
        """
        Captcha timeout decorator.

        This decorator can be used to decorate functions that must handle Captchas 
        that have not been solved in a given time.


        Example:

        bot = telebot.TeleBot(<Token>)
        captcha_manager = CaptchaManager()

        # Handles timed out Captchas
        @captcha_manager.on_captcha_timeout
        def on_captcha_timeout(captcha):
            if not captcha.solved:
                bot.send_message(captcha.chat.id, captcha.user.first_name + ' did not solve the Captcha!')

        Attention: You have to start the timeout handler at the end of your script 
        (above bot.polling())

        captcha_manager.start_timeout_handler()
        bot.polling()
        
        """
        def wrapper(*args, **kwargs):
            rv = function(*args, **kwargs)
            return rv
        self.__class__._handlers["on_timeout"] = wrapper
        for captcha in self.captchas.values():
            captcha._continue_timeout()
        return wrapper

    def _check_captcha(self, captcha: Captcha, bot: TeleBot):
        is_correct = captcha.users_code == captcha.correct_code
        captcha.previous_tries += 1

        if (captcha.options.max_incorrect_to_auto_reload >= captcha.incorrect_chars 
                and not is_correct 
                and captcha.previous_tries < captcha.options.max_attempts):
            captcha._reset(bot)
        else:
            if (captcha._timeout_thread):
                captcha._timeout_thread.cancel()
                captcha._timeout_thread = None

            if is_correct:
                self._handlers["on_correct"](captcha)
            else:
                self._handlers["on_not_correct"](captcha)
            captcha.solved = True


def _code_input_markup(captcha: Captcha) -> types.InlineKeyboardMarkup:
    values = {}
    row_width = 5
    display_attempts_left = captcha.options.max_attempts - captcha.previous_tries
    if captcha.options.max_incorrect_to_auto_reload <= 0:
        display_attempts_left = 0
    display_attempts_left = "" if display_attempts_left <= 0 else str (display_attempts_left)
    if captcha.options.generator == "keyzend":
        chars = extend_code(captcha.correct_code, 10)
        for char in chars:
            values[char] = {"callback_data": f"?cap={captcha.user.id}={char}"}
    else:
        chars = digits if captcha.options.only_digits else hexdigits
        for char in chars:
            values[char] = {"callback_data": f"?cap={captcha.user.id}={char}"}
        if not captcha.options.only_digits:
            row_width = 4
    if captcha.user_reloads_left > 0:
        values[f'🔄 {captcha.user_reloads_left}'] = {"callback_data": f"?cap={captcha.user.id}=RELOAD"}
    values = {**values,
        "⬅️": {"callback_data": f"?cap={captcha.user.id}=BACK"},
        f"✅ {display_attempts_left}": {"callback_data": f"?cap={captcha.user.id}=OK"}
    }
    return _quick_markup(values, row_width)

  
def _quick_markup(values, row_width=4) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    buttons = []
    for text, kwargs in values.items():
        buttons.append(types.InlineKeyboardButton(text=text, **kwargs))
    markup.add(*buttons)
    return markup

def _random_code(chars, length):
    code = ""
    while length > 0:
        if length >= len(chars):
            code += "".join(random.sample(chars, len(chars)))
            length -= len(chars)
        else:
            code += "".join(random.sample(chars, length))
            length = 0
    return code


def extend_code(code: str, target_length: int, chars: str="ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    result = []
    code: list = list(code.upper())
    chars: list = list(chars.upper())
    for c in code:
        if not c in result: 
            result.append(c)
            chars.remove(c)
    while len(result) < target_length:
        c = chars[random.randint(0,len(chars)-1)]
        result.append(c)
        chars.remove(c)
    random.shuffle(result)
    return result


def _random_codeimage(options: CaptchaOptions) -> Tuple:
    image, code = None, None
    if options.generator == "keyzend":
        r = requests.get("http://tyt.xyeta.ml/captcha.png")
        if r.status_code == 200:
            code = r.headers["answer"].upper()
            image = r.content
        else:
            raise requests.RequestException("Could not get the CAPTCHA from http://tyt.xyeta.ml/captcha.png")
    
    else:
        image = ImageCaptcha(300, 128, _fonts, [48, 42, 54])
        code = _random_code(digits if options.only_digits else hexdigits, options.code_length)
        image = image.generate_image(code)

    if options.add_noise:
        image = _add_noise(image)

    return (code, image)

def _add_noise(im: Image.Image, mean=12, sigma=48) -> Image.Image:
    for x in range(im.size[0]):
        for y in range (im.size[1]):
            r, g, b = im.getpixel((x, y))
            im.putpixel((x, y), (
                int(min(max(0, r + random.normalvariate(mean,sigma)), 255)),
                int(min(max(0, g + random.normalvariate(mean,sigma)), 255)),
                int(min(max(0, b + random.normalvariate(mean,sigma)), 255)),
            ))
    return im

def _escape(text: str) -> str:
    chars = {"&": "&amp;", "<": "&lt;", ">": "&gt"}
    for old, new in chars.items(): text = text.replace(old, new)
    return text

def _user_link(user: types.User, include_id: bool=False) -> str:
    name = _escape(user.first_name)
    return f"<a href='tg://user?id={user.id}'>{name}</a>" + (f" (<pre>{user.id}</pre>)" if include_id else "")

