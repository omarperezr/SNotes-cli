import os
import pathlib
import time
from datetime import datetime, timezone
from os import listdir
from os.path import isfile, join
from typing import Union

import keyboard

import proto_definitions.notes_pb2 as ProtoNote
from core.settings import settings
from Note import Note
from utils.utils import border_msg, del_password, get_login_cli


class NoteManager:
    def __init__(self) -> None:
        self.master_password = ""
        self.time_passed_since_last_login()
        _, password = get_login_cli()
        self.master_password = password

    def write(self, modify: bool = False) -> Note:
        '''
            Creates a new note
        '''
        title = input("\nTitle: ")

        if modify:
            note_to_mod = self.get_note_from_proto(title.lower().strip())
            keyboard.write(note_to_mod.body)

        body = input("Body: ")
        isSecret = input("Encrypt? N/y: ").lower().strip()

        if isSecret == "y":
            isSecret = True
        else:
            isSecret = False

        new_note = Note(title, body, isSecret, self.master_password)
        new_note.serialize()

        return new_note

    def delete(self, title: str) -> None:
        '''
            Deletes a note by title
        '''
        all_notes = self.get_all_note_files()
        note_filepath = pathlib.Path(settings.DATA_PATH, all_notes[title])
        os.remove(note_filepath)

    def delete_all(self) -> None:
        '''
            Deletes all notes
        '''
        all_notes = self.get_all_note_files()
        for title in all_notes:
            note_filepath = pathlib.Path(settings.DATA_PATH, all_notes[title])
            os.remove(note_filepath)

    def get_all_note_files(self) -> dict:
        '''
            Returns a dictionary with all the note titles as key and file name as value
        '''
        onlyfiles = {f.replace(";", " "): f for f in listdir(
            settings.DATA_PATH) if isfile(join(settings.DATA_PATH, f))}
        return onlyfiles

    def show_all_notes(self) -> dict:
        '''
            Reads the configured path where all the proto serialized notes reside
            and returns the correct title name and modified date for all the notes
        '''
        all_stored_notes = self.get_all_note_files()
        print()
        print("Notes".rjust(7), "Modification date".rjust(65))
        print("-"*80)
        print()
        for n in all_stored_notes.keys():
            modified_time = datetime.fromtimestamp(pathlib.Path(
                settings.DATA_PATH, all_stored_notes[n]).stat().st_mtime, tz=timezone.utc).strftime('%Y-%m-%d')
            print(f" {n}".ljust(25), "-".ljust(40, "-"), modified_time)

        return all_stored_notes

    def get_notes(self) -> Note:
        '''
            Shows a prompt with all the notes to select one note, it opens the proto note stored in the configured path
            if the note is encrypted it will decrypt it automaticaly with the  master password and print it 
            otherwise it will simply print it
        '''
        all_notes = self.show_all_notes()
        note_title = input("\n: ").lower().strip()

        if note_title not in all_notes:
            print("That note does not exist")
            return None
        return self.get_note_from_proto(note_title)

    def get_note_from_proto(self, title: str) -> Union[Note, None]:
        '''
            Gets one Note selected by title
        '''
        all_notes = self.get_all_note_files()
        if not title in all_notes:
            return None
        note_filepath = pathlib.Path(settings.DATA_PATH, all_notes[title])
        proto_note = ProtoNote.Note()
        with open(note_filepath, "rb") as fd:
            proto_note.ParseFromString(fd.read())

        python_note = Note(proto_note, self.master_password)
        return python_note

    def print_note(self, note: Note) -> None:
        '''
            Prints formatted data for a selected note
        '''
        note_str = f"Body: {note.body}\nIs encrypted?: {note.isSecret}"
        note_str = border_msg(note_str, title=note.title)
        print(note_str)

    def time_passed_since_last_login(self):
        note = self.get_note_from_proto("__passdate__")
        if note:
            username, _ = get_login_cli()
            last_entered_password_time = int(note.body)
            mult_by = {"h": 3600, "m": 60, "s": 1}
            time_unit = settings.PASSWORD_EXPIRATION[-1]
            time_limit = int(
                settings.PASSWORD_EXPIRATION[:-1]) * mult_by[time_unit]

            if last_entered_password_time + time_limit <= int(time.time()):
                del_password(username)
                Note("__passdate__", str(int(time.time())), False, "").serialize()
        else:
            Note("__passdate__", str(int(time.time())), False, "").serialize()