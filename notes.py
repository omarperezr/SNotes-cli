import base64
import shelve
import tkinter as tk
from binascii import Error as binasciiError
from datetime import datetime
from dbm import error as dbmError
from hashlib import sha256
from os import mkdir

from Crypto import Random
from Crypto.Cipher import AES

__all__ = ['Note', 'new_note', 'modify_note', 'search_note', 'show_all_notes', 'del_note', 'del_all',
            'usage', 'AESCipher', 'dbmError']

dbmError = dbmError        # Error raised when having problems with shelve

class Note:
    """ Defines the all the data that a note has and functions that return that data """
    def __init__(self, cod, title, text):
        self.cod = cod
        self.title = title
        self.text = text
        self.date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def __str__(self):
        return f'''
#############################################
ID: {self.cod}
Title: {self.title}
Note: {self.text}

Last modification: {self.date}
############################################'''

    def get_data(self):
        """ Returns a string with al the data in a Note """
        return f"{self.title} {self.cod} {self.text}"


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
        """ Does the inverse of pad """
        return s[0:-s[-1]]

    def encrypt(self, note_text):
        """ Returns a string encrypted with AES """
        note_text = self.pad(note_text)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(note_text))

    def decrypt(self, note_cod):
        """ Prints a string decrypted with AES """
        try:
            with shelve.open("./data/notes", "r") as notes_db:
                enc = base64.b64decode(notes_db[note_cod].text)
                iv = enc[:16]
                cipher = AES.new(self.key, AES.MODE_CBC, iv)
                print(f'''
###########################################
ID: {notes_db[note_cod].cod}
Title: {notes_db[note_cod].title}
Text: {self.unpad(cipher.decrypt(enc[16:])).decode('UTF-8')}
###########################################''')
        except KeyError:
            print(f"\nNo note with the id {note_cod} exists")
        except binasciiError:
            print("\nThat note can't be decrypted")


def get_total_notes():
    """ Returns the total of notes created """
    try:
        with shelve.open('./data/notes', 'r') as notes_db:
            total_notes = notes_db['total']
    except dbmError:
        mkdir("./data")
        with shelve.open("./data/notes") as notes_db:
            notes_db["total"] = total_notes = 0

    return total_notes


def show_all_notes():
    """ Prints every note that has been saved """
    with shelve.open('./data/notes', 'r') as notes_db:
        if len(notes_db) > 1:
            for i in notes_db:
                if i != "total":
                    print(notes_db[i])
        else:
            print("\nThere are no notes nor reminders available")


def new_note(note_title, note_text):
    """ Creates a new Note objects and serializes it """
    note_cod = f'n{get_total_notes()+1}'
    with shelve.open("./data/notes") as notes_db:
        notes_db['total'] += 1
        notes_db[str(note_cod)] = Note(note_cod, note_title, note_text)
        print(notes_db[str(note_cod)])

def modify_note(note_cod):
    """ Modifies an already created note selected by ID """
    with shelve.open("./data/notes") as notes_db:
        note_text = notes_db[note_cod].text

        modify_window = tk.Tk()
        modify_window.title(f"Modifying note '{note_cod}'")
        
        mnote_text = tk.StringVar()
        mnote_text.set(note_text)

        mnote_text_entry = tk.Entry(modify_window, textvariable = mnote_text).grid(row=1, column=0, padx=5, pady=5)

        modify_window.mainloop()

def del_note(note_cod):
    """ Deletes a Note object from the database selected by ID """
    with shelve.open("./data/notes") as notes_db:
        if notes_db.pop(str(note_cod), -1) == -1:
            print("\nNo note with ID:", note_cod)


def search_note(note_info):
    """ Searches for a note in the database by ID """
    with shelve.open('./data/notes', 'r') as notes_db:
        if len(notes_db) > 1:

            for i in notes_db:
                if i != "total" and note_info in notes_db[i].get_data():
                    print(notes_db[i])
        else:
            print("\nThere are no notes nor reminders with that data")


def del_all():
    """ Deletes every note created """
    with shelve.open("./data/notes", 'n') as notes_db:
        notes_db['total'] = 0


def usage():
    """ Prints the usage of nterm and examples """
    print('''
usage: nterm [OPTION] [<ARGUMENTS>]

    -n, --note              Creates a new note with title and text
    -p, --encrypt           Use this flag after a note to encrypt it with a password
    -u, --decrypt           Use this flag to decrypt your note a the password
    -r, --reminder          Creates a new reminder
    -s, --search            Searches for a note or reminder by id, title and text (CASE SENSITIVE)
    -l, --list              Shows a list of every note and reminder sorted by modification
    -d, --delete            Deletes an specified note or reminder by id
    -D, --delete-all        Deletes EVERY note and reminder saved
    -h, --help              Shows this help document
        
examples:
    >   nterm --note "The title" "This is the text of the note"
    >   nterm --note "The title" "This is a secret message" --encrypt "This is the password"
    >   nterm --note n1 --decrypt "The password I used"
    >   nterm --list
    >   nterm --delete n1
    >   nterm --delete-all
    >   nterm --search n1''')
