import pathlib
from datetime import datetime, timezone
from os import listdir
from os.path import isfile, join

import proto_definitions.notes_pb2 as ProtoNote
from core.settings import settings
from Note import Note


class NoteManager:
    def __init__(self, master_password) -> None:
        self.master_password = master_password

    def new_note(self):
        '''
            Creates a new note
        '''
        print()
        title = input("Title: ")
        body = input("Body: ")
        isSecret = input("Encrypt? N/y: ").lower().strip()

        if isSecret == "y":
            isSecret = True
        else:
            isSecret = False

        Note(title, body, isSecret, self.master_password).serialize()

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
            modified_time = datetime.fromtimestamp(pathlib.Path(settings.DATA_PATH,all_stored_notes[n]).stat().st_mtime, tz=timezone.utc).strftime('%Y-%m-%d')
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
        print(f"Title: {note.title}\nBody: {note.body}\nIs encrypted?: {note.isSecret}")

