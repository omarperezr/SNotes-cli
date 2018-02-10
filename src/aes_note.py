import shelve
from base64 import b64decode, b64encode
from hashlib import sha256

from Crypto.Cipher import AES


class AESCipher:
    """ Encrypts text with the AES algorithm """
    def __init__(self, key):
        self.bs = 16
        self.key = sha256(key.encode('UTF-8')).digest()

    def pad(self, s):
        """ Takes a string and makes sure it is a multiple of bs and alters it if it isn't """
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def unpad(s):
        return s[0:-s[-1]]

    def encrypt(self, note_text):
        from Crypto import Random
        note_text = self.pad(note_text)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return b64encode(iv + cipher.encrypt(note_text))

    def decrypt(self, note_cod):
        from note import pretty_string
        with shelve.open("./data/notes", "r") as notes_db:
            if note_cod in notes_db:
                enc = b64decode(notes_db[note_cod].text)
                iv = enc[:16]
                cipher = AES.new(self.key, AES.MODE_CBC, iv)
                print(pretty_string('''
ID: {} Title: {}
---------------------------------------------------------
Text: {}
---------------------------------------------------------'''.format(notes_db[note_cod].cod,\
                                                             notes_db[note_cod].title[:20],\
                                                             self.unpad(cipher.decrypt(enc[16:])).decode('UTF-8'))))
            else:
                print("No note with the id {}".format(note_cod))
