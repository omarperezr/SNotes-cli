from email.policy import default
import sys

from NoteManager import NoteManager
from utils.utils import clip_copy, del_password


def main():
    usage = """
    Usage:
        nterm.py [-n | --new] [-m | --modify] [-s | --select]
        nterm.py [-g | --get] [-d | --delete] "<note title>"

    Options:
        -n | --new              Creates new note
        -m | --modify           Modifies existing note
        -d | --delete           Creates new note
        -g | --get              Gets a note by title
        -s | --select           Shows prompt with all notes to select one by title  
    """

    note_manager = NoteManager()

    args = [a.lower() for a in sys.argv[1:]]

    if len(args) == 0:
        print(usage)

    elif len(args) == 1:
        if args[0] in ('-n', '--new'):
            # New
            new_note = note_manager.write()
            note_manager.print_note(new_note)
        elif args[0] in ('-m', '--modify'):
            # Modify
            new_note = note_manager.write(modify=True)
            note_manager.print_note(new_note)
        elif args[0] in ('-s', '--select'):
            # Select prompt
            note_selected = note_manager.get_notes()
            note_manager.print_note(note_selected)
            clip_copy(note_selected.body)

    elif len(args) == 2:
        if args[0] in ('-g', '--get'):
            # Get by title
            note = note_manager.get_note_from_proto(args[1])
            note_manager.print_note(note)
            clip_copy(note.body)
        elif args[0] in ('-d', '--delete'):
            # Delete by title
            note_manager.delete(args[1])
            print(f"{args[1]} deleted!")
    else:
        print(usage)


if __name__ == '__main__':
    main()
