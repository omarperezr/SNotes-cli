import pathlib
from hashlib import sha256

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

import proto_definitions.notes_pb2 as ProtoNote
from core.settings import settings


class Note:
    def __init__(self, *args):
        '''
            Class in charge of serializing and encrypting/decrypting notes
            *args can be title: str, body: str and isSecret: bool in that order or a ProtoNote.Note object
        '''
        if isinstance(args[0], ProtoNote.Note):
            self.title = args[0].title
            self.body = args[0].body
            self.encryptedBody = args[0].encryptedBody
            self.isSecret = args[0].isSecret
            self.master_password = sha256(args[1].encode('UTF-8')).digest()

            if self.isSecret:
                self.decrypt()
        else:
            self.title = args[0]
            self.body = args[1]
            self.isSecret = args[2]
            self.master_password = sha256(args[3].encode('UTF-8')).digest()

            if self.isSecret:
                self.encrypt()

    def serialize(self) -> None:
        serialized_note = ProtoNote.Note()
        serialized_note.title = self.title
        if self.isSecret:
            serialized_note.encryptedBody = self.body
        else:
            serialized_note.body = self.body
        serialized_note.isSecret = self.isSecret

        filepath = pathlib.Path(settings.DATA_PATH, self.title_to_filename())
        with open(filepath, "wb") as fd:
            fd.write(serialized_note.SerializeToString())

    def encrypt(self) -> None:
        encryptor = Cipher(algorithms.AES(
            self.master_password), modes.ECB()).encryptor()
        padder = padding.PKCS7(algorithms.AES(
            self.master_password).block_size).padder()
        padded_data = padder.update(
            self.body.encode('utf-8')) + padder.finalize()
        encrypted_text = encryptor.update(padded_data) + encryptor.finalize()
        self.body = encrypted_text

    def decrypt(self) -> None:
        decryptor = Cipher(algorithms.AES(
            self.master_password), modes.ECB()).decryptor()
        padder = padding.PKCS7(algorithms.AES(
            self.master_password).block_size).unpadder()
        decrypted_data = decryptor.update(self.encryptedBody)
        unpadded = padder.update(decrypted_data) + padder.finalize()
        self.body = unpadded.decode('utf-8')

    def title_to_filename(self) -> str:
        file_name = self.title.lower().replace(";", "")
        return file_name.replace(" ", ";")
