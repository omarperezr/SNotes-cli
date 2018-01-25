import shelve
from datetime import datetime

import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


__all__ = ['Note', 'termn_usage', 'new_note', 'search_note', 'show_all_notes', 'del_note', 'del_all',
           'AESCipher']


class AESCipher:
    def __init__(self, key):
        self.bs = 16
        self.key = hashlib.sha256(key.encode('UTF-8')).digest()

    def pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def unpad(s):
        return s[0:-s[-1]]

    def encrypt(self, note_text):
        note_text = self.pad(note_text)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(note_text))

    def decrypt(self, note_cod):
        try:
            with shelve.open("./data/notes", "r") as notes_db:
                enc = base64.b64decode(notes_db[note_cod].text)
                iv = enc[:16]
                cipher = AES.new(self.key, AES.MODE_CBC, iv)
                print(self.unpad(cipher.decrypt(enc[16:])).decode('UTF-8'))
        except KeyError:
            print(f"\nNo note with the id {note_cod} exists")


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
        return self.title + " " + self.cod + " " + self.text.decode("UTF-8")


def termn_usage():
    print('''
    usage: termn [OPTION] [<ARGUMENTS>]

        -n, --note              Creates a new note with title and text
        -p, --encrypt           Use this flag after a note to encrypt it with the password after the flag
        -u, --decrypt           Use this flag to decrypt your note with the password after the flag
        -r, --reminder          Creates a new reminder
        -s, --search            Searches for a note or reminder by id, title and text (CASE SENSITIVE)
        -l, --list              Shows a list of every note and reminder sorted by modification
        -d, --delete            Deletes an specified note or reminder by id
        -D, --delete-all        Deletes EVERY note and reminder saved
        -h, --help              Shows this help document
        
    examples:
        termn -n "Test 1" "Omar is really a nice man"                               <-- Creates a new note
        termn -n "Test 2" "This is a super secret message" -p "This is a password"  <-- Creates an encrypted note
        termn -n -u n1 "the password i used"                                        <-- Decrypts an encrypted note
        termn -s n1                                                                 <-- Search for a note with id n1
        termn -l                                                                    <-- Lists every note
        termn -d n1                                                                 <-- Deletes a note with id n1
        termn -D                                                                    <-- Deletes every note''')


def get_total_notes():
    try:
        with shelve.open('./data/notes', 'r') as notes_db:
            total_notes = notes_db['total']
    except  Exception:
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
