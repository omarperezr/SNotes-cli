import getpass

import keyring
import pyperclip
from core.settings import settings
import time


def border_msg(msg, indent=1, width=None, title=None):
    '''
        Print message-box with optional title
    '''
    lines = msg.split('\n')
    space = " " * indent
    if not width:
        width = max(map(len, lines))
    box = f'╔{"═" * (width + indent * 2)}╗\n'  # upper_border
    if title:
        box += f'║{space}{title:<{width}}{space}║\n'  # title
        box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore
    box += ''.join([f'║{space}{line:<{width}}{space}║\n' for line in lines])
    box += f'╚{"═" * (width + indent * 2)}╝'  # lower_border
    return box


def clip_copy(text):
    isCopy = input("Copy to clipboard? N/y: ").lower().strip()

    if isCopy == "y":
        pyperclip.copy(text)


def get_login_cli(username=None, prompt=False):
    '''
    Get the password for the username out of the keyring.  If the password
    isn't found in the keyring, ask for it from the command line
    '''
    disp_username = False

    if username is None or prompt:
        username = getpass.getuser()
        disp_username = True

    passwd = keyring.get_password(settings.PROJECT_TITLE, username)

    if passwd is None or prompt:
        if disp_username:
            print(f'Username: {username}')

        passwd = getpass.getpass()
        set_password(username, passwd)

    return (username, passwd)


def set_password(username, passwd):
    '''
    Writes the password to the keyring
    '''
    keyring.set_password(settings.PROJECT_TITLE, username, passwd)


def del_password(username):
    '''
    Deletes the password from the keyring
    '''
    keyring.delete_password(settings.PROJECT_TITLE, username)    
