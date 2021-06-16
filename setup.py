from setuptools import setup

long_description = None
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='pyTelegramBotCAPTCHA',
    packages=['pyTelegramBotCAPTCHA'],
    version='0.1.3',
    author='SwissCorePy',
    author_email='swisscore.py@gmail.com',

    license='gpl-3.0',
    description='An easy to use an (hopefully useful) captcha solution for pyTelegramBotAPI.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    package_dir={'pyTelegramBotCAPTCHA': 'pyTelegramBotCAPTCHA'},
    include_package_data=True,

    url='https://github.com/SwissCorePy/pyTelegramBotCAPTCHA',
    download_url='https://github.com/SwissCorePy/pyTelegramBotCAPTCHA/archive/refs/heads/main.zip',

    keywords=['Telegram', 'Captcha', 'pyTelegramBotAPI'],
    install_requires=['pyTelegramBotAPI==3.7.7', 'captcha', 'Pillow'],
    extras_require={'json': 'ujson'},
    
    classifiers=[
        # "3 - Alpha", "4 - Beta", "5 - Production/Stable"
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3'
    ],
)
