import argparse
from textwrap import fill as tfill

__all__ = ['argparse', 'CreateNote', 'CreateEncryptedNote', 'DecryptNote', 'ModifyNote', 'ShowNote',
           'ListAll', 'RemoveNote', 'RemoveAll']


def pretty_string(string):
    return tfill(string, width=57, replace_whitespace=False)


class Note:
    """ Defines the all the data that a note has and functions that return that data """
    def __init__(self, cod, title, text):
        from datetime import datetime
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


class CreateNote(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        import shelve
        with shelve.open("./data/notes") as notes_db:
            notes_db['total'] += 1
            note_cod = f'n{notes_db["total"]}'
            notes_db[note_cod] = Note(note_cod, values[0], values[1])
            print(f'\n{pretty_string(str(notes_db[note_cod]))}')


class CreateEncryptedNote(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        from aes_note import AESCipher, shelve
        cipher = AESCipher(values[2])
        with shelve.open("./data/notes") as notes_db:
            notes_db['total'] += 1
            note_cod = f'e{notes_db["total"]}'
            notes_db[note_cod] = Note(note_cod, values[0], cipher.encrypt(values[1]).decode('UTF-8'))
            print(f'\n{pretty_string(str(notes_db[note_cod]))}')


class DecryptNote(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        from aes_note import AESCipher
        cipher = AESCipher(values[1])
        cipher.decrypt(values[0])


class ModifyNote(argparse.Action):
    """ Modifies an available note selected by ID """
    def __call__(self, parser, namespace, value, option_string=None):
        from note_mod import mod_note
        if value[0] != 'e':
            mod_note(value)
        else:
            print("You can't edit an encrypted note")


class RemoveNote(argparse.Action):
    """ Deletes n notes from the database selected by ID """
    def __call__(self, parser, namespace, values, option_string=None):
        import shelve
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
        import shelve
        with shelve.open("./data/notes", 'n') as notes_db:
            notes_db['total'] = 0
        print("\nAll notes removed")


class ShowNote(argparse.Action):
    """ Searches for a note in the database by ID, Title and string in text """
    def __call__(self, parser, namespace, value, option_string=None):
        import shelve
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
        import shelve
        with shelve.open('./data/notes', 'r') as notes_db:
            if len(notes_db) > 1:
                print("\n\tPress <Enter> to show the next note")
                for i in list(notes_db.values())[1:]:
                    print(f'\n{pretty_string(i.shorter_str())}')
                    input()
            else:
                print("\nThere are no notes available")
