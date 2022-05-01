import pathlib
from datetime import datetime, timezone
import os
from os import listdir
from os.path import isfile, join

import proto_definitions.notes_pb2 as ProtoNote
from core.settings import settings
from Note import Note
import keyboard
from utils.utils import border_msg, get_login_cli


class NoteManager:
    def __init__(self) -> None:
        username, password = get_login_cli()
        self.master_password = password

    def write_note(self, modify: bool = False) -> Note:
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

    def delete_note(self, title):
        all_notes = self.get_all_note_files()
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

    def get_note_from_proto(self, title: str) -> Note:
        '''
            Gets one Note selected by title
        '''
        all_notes = self.get_all_note_files()
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
        note_str = f"Title: {note.title}\nBody: {note.body}\nIs encrypted?: {note.isSecret}"
        note_str = border_msg(note_str)
        print(note_str)
