import shelve
import tkinter as tk

from note import Note, pretty_string


def mod_note(value):
    with shelve.open('./data/notes', 'r') as notes_db:
        if value in notes_db:
            root = tk.Tk()
            root.title(f"Note {value}")
            NoteModifyWindow(root, value).pack(side="top", fill="both", expand=True)
            root.mainloop()
        else:
            print(f"\nNo note with ID {value}")

class NoteModifyWindow(tk.Frame):
    """ Creates a window to modify an already created note selected by ID """
    def __init__(self, parent, note_cod, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.note_cod = note_cod
        self.note_title = self.get_note_title()
        self.note_text = self.get_note_text()

        self.var_title = tk.StringVar()
        self.var_title.set(self.note_title)

        self.tk_note_title_entry = tk.Entry(self, textvariable=self.var_title).\
            pack(fill='x', expand=True, padx=3, pady=3, ipadx=20, ipady=2)  # Note title widget Entry

        self.tk_note_text_entry = tk.Text(self, width=57, height=23)        # Note text widget Text
        self.tk_note_text_entry.insert('insert', self.note_text)
        self.tk_note_text_entry.pack()

        self.tk_note_text_button = tk.Button(self, bg="sky blue", text="Modify", command=self.save_modified_note).\
            pack(fill='x', expand=True, padx=3, pady=3, ipadx=20, ipady=15)  # Modify Button

    def get_note_text(self):
        with shelve.open("./data/notes") as notes_db:
            return notes_db[self.note_cod].text

    def get_note_title(self):
        with shelve.open("./data/notes") as notes_db:
            return notes_db[self.note_cod].title

    def save_modified_note(self):
        """ Saves the modified text to the database """
        with shelve.open("./data/notes") as notes_db:
            notes_db[self.note_cod] = Note(notes_db[self.note_cod].cod, self.var_title.get(),
                                           self.tk_note_text_entry.get("1.0", 'end').rstrip('\n'))
            print(pretty_string(str(notes_db[self.note_cod])))
        self.quit()
