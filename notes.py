import argparse
import shelve
import tkinter as tk
from base64 import b64decode, b64encode
from binascii import Error as binasciiError
from datetime import datetime
from hashlib import sha256
from textwrap import fill as tfill

from Crypto import Random
from Crypto.Cipher import AES

__all__ = ['argparse', 'CreateNote', 'CreateEncryptedNote', 'DecryptNote', 'ModifyNote', 'ShowNote',
           'ListAll', 'RemoveNote', 'RemoveAll']


def pretty_string(string):
    return tfill(string, width=57, replace_whitespace=False)


class Note:
    """ Defines the all the data that a note has and functions that return that data """
    def __init__(self, cod, title, text):
        self.cod = cod
        self.title = title
        self.text = text
        self.date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def __str__(self):
        return f'''
ID: {self.cod}                              {self.date}
---------------------------------------------------------
Title: {self.title}
    
    {self.text}
---------------------------------------------------------
'''

    def shorter_str(self):
        return f'''
ID: {self.cod}                              {self.date}
---------------------------------------------------------
Title: {self.title}
    
    {self.text[:77]} ...
---------------------------------------------------------
'''


class AESCipher:
    """ Encrypts text with the AES algorithm """
    def __init__(self, key):
        self.bs = 16
        self.key = sha256(key.encode('UTF-8')).digest()

    def pad(self, s):
        """ Takes a string and makes sure it is a multiple of bs and alters it if it isn't """
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def unpad(s):
        return s[0:-s[-1]]

    def encrypt(self, note_text):
        note_text = self.pad(note_text)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return b64encode(iv + cipher.encrypt(note_text))

    def decrypt(self, note_cod):
        with shelve.open("./data/notes", "r") as notes_db:
            if note_cod in notes_db:
                try:
                    enc = b64decode(notes_db[note_cod].text)
                    iv = enc[:16]
                    cipher = AES.new(self.key, AES.MODE_CBC, iv)
                    print(pretty_string(f'''
ID: {notes_db[note_cod].cod} Title: {notes_db[note_cod].title[:20]}
---------------------------------------------------------
Text: {self.unpad(cipher.decrypt(enc[16:])).decode('UTF-8')}
---------------------------------------------------------'''))
                except binasciiError:
                    print("\nThat note can't be decrypted")
            else:
                print(f"\nNo note with the id {note_cod}")


class NoteModifyWindow(tk.Frame):
    """ Creates a window to modify an already created note selected by ID """
    def __init__(self, parent, note_cod, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.note_cod = note_cod
        self.note_title = self.get_note_title()
        self.note_text = self.get_note_text()

        self.var_title = tk.StringVar()
        self.var_title.set(self.note_title)

        self.tk_note_title_entry = tk.Entry(self, textvariable=self.var_title).\
            pack(fill='x', expand=True, padx=3, pady=3, ipadx=20, ipady=2)  # Note title widget Entry

        self.tk_note_text_entry = tk.Text(self, width=57, height=23)        # Note text widget Text
        self.tk_note_text_entry.insert('insert', self.note_text)
        self.tk_note_text_entry.pack()

        self.tk_note_text_button = tk.Button(self, bg="sky blue", text="Modify", command=self.save_modified_note).\
            pack(fill='x', expand=True, padx=3, pady=3, ipadx=20, ipady=15)  # Modify Button

    def get_note_text(self):
        with shelve.open("./data/notes") as notes_db:
            return notes_db[self.note_cod].text

    def get_note_title(self):
        with shelve.open("./data/notes") as notes_db:
            return notes_db[self.note_cod].title

    def save_modified_note(self):
        """ Saves the modified text to the database """
        with shelve.open("./data/notes") as notes_db:
            notes_db[self.note_cod] = Note(notes_db[self.note_cod].cod, self.var_title.get(),
                                           self.tk_note_text_entry.get("1.0", 'end').rstrip('\n'))
            print(notes_db[self.note_cod])
        self.quit()


def new_note(note_title, note_text):
    """ Creates a new Note objects and serializes it """
    with shelve.open("./data/notes") as notes_db:
        note_cod = f'n{notes_db["total"]+1}'
        notes_db['total'] += 1
        notes_db[note_cod] = Note(note_cod, note_title, note_text)
        print(f'\n{pretty_string(str(notes_db[note_cod]))}')

# Custom Argparse Functions


class CreateNote(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        new_note(values[0], values[1])


class CreateEncryptedNote(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        cipher = AESCipher(values[2])
        new_note(values[0], cipher.encrypt(values[1]).decode('UTF-8'))


class DecryptNote(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        cipher = AESCipher(values[1])
        cipher.decrypt(values[0])


class ModifyNote(argparse.Action):
    """ Modifies an available note selected by ID """
    def __call__(self, parser, namespace, value, option_string=None):
        with shelve.open('./data/notes', 'r') as notes_db:
            if value in notes_db:
                root = tk.Tk()
                root.title(f"Note {value}")
                NoteModifyWindow(root, value).pack(side="top", fill="both", expand=True)
                root.mainloop()
            else:
                print(f"\nNo note with ID {value}")


class RemoveNote(argparse.Action):
    """ Deletes n notes from the database selected by ID """
    def __call__(self, parser, namespace, values, option_string=None):
        with shelve.open("./data/notes") as notes_db:
            if len(notes_db) > 1:
                for note_cod in values:
                    if notes_db.pop(note_cod, -1) == -1:
                        print(f"\nNo note with ID: {note_cod}")
                    else:
                        print(f"\nNote {note_cod} removed")
            else:
                print("\nThere are no notes available")


class RemoveAll(argparse.Action):
    """ Deletes every note created """
    def __call__(self, parser, namespace, values, option_string=None):
        with shelve.open("./data/notes", 'n') as notes_db:
            notes_db['total'] = 0
        print("\nAll notes removed")


class ShowNote(argparse.Action):
    """ Searches for a note in the database by ID, Title and string in text """
    def __call__(self, parser, namespace, value, option_string=None):
        with shelve.open('./data/notes', 'r') as notes_db:
            if len(notes_db) > 1:
                if value in notes_db:
                    print(f'\n{pretty_string(str(notes_db[value]))}')
                else:
                    print(f"\nThere is no note with ID {value}")
            else:
                print("\nThere are no notes available")


class ListAll(argparse.Action):
    """ Shows every available note """
    def __call__(self, parser, namespace, values, option_string=None):
        with shelve.open('./data/notes', 'r') as notes_db:
            if len(notes_db) > 1:
                print("\n\tPress <Enter> to show the next note")
                for i in list(notes_db.values())[1:]:
                    print(f'\n{pretty_string(i.shorter_str())}')
                    input()
            else:
                print("\nThere are no notes available")
