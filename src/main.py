from core.settings import settings
from NoteManager import NoteManager

note_manager = NoteManager(settings.MASTER_PASSWORD)
note_manager.new_note()
note_selected = note_manager.get_note()
note_manager.print_note(note_selected)
