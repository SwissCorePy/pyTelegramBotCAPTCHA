try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pyTelegramBotCAPTCHA',
    packages=['pyTelegramBotCAPTCHA'],
    version='0.0.17',
    license='gpl-3.0',
    description='An easy to use an (hopefully useful) captcha solution for pyTelegramBotAPI.',
    author='SwissCorePy',
    author_email='swisscore.py@gmail.com',
    
    #package_data = {'data': ['*.json', '*.ttf'],},
    #include_package_data=True,
    package_dir={'pyTelegramBotCAPTCHA': 'pyTelegramBotCAPTCHA'},
    
    url='https://github.com/SwissCorePy/pyTelegramBotCAPTCHA',
    download_url='https://github.com/SwissCorePy/pyTelegramBotCAPTCHA/archive/refs/heads/main.zip',

    keywords=['Telegram', 'Captcha', 'pyTelegramBotAPI'],
    install_requires=['pyTelegramBotAPI', 'captcha', 'Pillow'],
    extras_require={'json': 'ujson'},
    
    classifiers=[
        # "3 - Alpha", "4 - Beta", "5 - Production/Stable"
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3'
    ],
)
