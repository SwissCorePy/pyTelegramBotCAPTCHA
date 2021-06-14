from setuptools import setup
setup(
    name='pyTelegramBotCAPTCHA',
    packages=['pyTelegramBotCAPTCHA'],
    version='0.0.1',
    license='gpl-3.0',
    description='An easy to use an (hopefully useful) captcha solution for pyTelegramBotAPI.',
    author='SwissCorePy',
    author_email='swisscore.py@gmail.com',

    url='https://github.com/SwissCorePy/pyTelegramBotCAPTCHA',
    download_url='https://github.com/SwissCorePy/pyTelegramBotCAPTCHA/archive/refs/heads/main.zip',

    keywords=['Telegram', 'Captcha', 'pyTelegramPotAPI'],
    install_requires=['pyTelegramBotAPI', 'captcha', 'Pillow'],
    extras_require={'json': 'ujson'},
    
    classifiers=[
        # "3 - Alpha", "4 - Beta", "5 - Production/Stable"
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Telegram Bot Developers',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3.0',
        'Programming Language :: Python :: 3'
    ],
)
