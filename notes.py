import shelve
from os import mkdir
from dbm import error
from datetime import datetime

from hashlib import sha256
from base64 import b64encode, b64decode
from Crypto import Random
from Crypto.Cipher import AES


__all__ = ['Note', 'new_note', 'search_note', 'show_all_notes', 'del_note', 'del_all', 'nterm_usage',
           'AESCipher', 'dbmError']

dbmError = error


class Note:
    def __init__(self, cod, title, text, date):
        self.cod = cod
        self.title = title
        self.text = text
        self.date = date

    def __str__(self):
        return f'''
#############################################
ID: {self.cod}
Title: {self.title}
Note: {self.text}

Last modification: {self.date}
############################################'''

    def get_data(self):
        return f"{self.title} {self.cod} {self.text}"


class AESCipher:
    def __init__(self, key):
        self.bs = 16
        self.key = sha256(key.encode('UTF-8')).digest()

    def pad(self, s):
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
        try:
            with shelve.open("./data/notes", "r") as notes_db:
                enc = b64decode(notes_db[note_cod].text)
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


def nterm_usage():
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


def get_total_notes():
    try:
        with shelve.open('./data/notes', 'r') as notes_db:
            total_notes = notes_db['total']
    except dbmError:
        mkdir("./data")
        with shelve.open("./data/notes") as notes_db:
            notes_db["total"] = total_notes = 0

    return total_notes


def show_all_notes():
    with shelve.open('./data/notes', 'r') as notes_db:
        if len(notes_db) > 1:
            for i in notes_db:
                if i != "total":
                    print(notes_db[i])
        else:
            print("\nThere are no notes nor reminders available")


def new_note(note_title, note_text):
    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")             # The current date and time when creating the note
    note_cod = f'n{get_total_notes()+1}'
    with shelve.open("./data/notes") as notes_db:                               # Open the notes database
        notes_db['total'] += 1                                                  # Add 1 to the total of notes created
        notes_db[str(note_cod)] = Note(note_cod, note_title, note_text, date)   # Add the new note to the database
        print(notes_db[str(note_cod)])                                          # Print the new note


def del_note(note_cod):
    with shelve.open("./data/notes") as notes_db:
        if notes_db.pop(str(note_cod), -1) == -1:
            print("\nNo note with ID:", note_cod)


def search_note(note_info):
    with shelve.open('./data/notes', 'r') as notes_db:
        if len(notes_db) > 1:

            for i in notes_db:
                if i != "total" and note_info in notes_db[i].get_data():
                    print(notes_db[i])
        else:
            print("\nThere are no notes nor reminders with that data")


def del_all():
    with shelve.open("./data/notes", 'n') as notes_db:
        notes_db['total'] = 0
