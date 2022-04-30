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
        print("Notes".rjust(7), "Modification date".rjust(57))
        print("-"*67)
        print()
        for n in all_stored_notes.keys():
            modified_time = datetime.fromtimestamp(pathlib.Path(settings.DATA_PATH,all_stored_notes[n]).stat().st_mtime, tz=timezone.utc).strftime('%Y-%m-%d')
            print(f" {n}".ljust(15), "-".ljust(40, "-"), modified_time)

        return all_stored_notes

    def get_note(self) -> Note:
        '''
            Shows a prompt for the user to select a note, it opens the proto note stored in the configured path
            if the note is encrypted it will decrypt it automaticaly with the  master password and print it 
            otherwise it will simply print it
        '''
        all_notes = self.show_all_notes()
        note_title = input("\n:")

        note_filepath = pathlib.Path(settings.DATA_PATH, all_notes[note_title])

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

