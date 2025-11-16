from passlib.hash import pbkdf2_sha256
from cryptography.fernet import Fernet
import os
import base64
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


class PasswordIncorrectError(ValueError):
    pass


class InitializationError(ValueError):
    pass


class PasswordManager:
    def __init__(self, password, path="passwords.txt"):
        if os.path.exists(path):
            self._salt = None
            self._master_hash = ""
            self._pass_path = path
            self._storage = ""
            self._unlocked = False
            try:
                self.load_storage(password, path)
                print("База паролей успешно загружена")
                return
            except PasswordIncorrectError:
                raise PasswordIncorrectError("Неверный пароль!")

            except Exception as e:
                raise InitializationError(str(e))
        else:
            self._salt = os.urandom(16)
            self._master_hash = self.hash_password(password)
            self._pass_path = path
            self._storage = ""
            self._unlocked = False
            self.save_storage(password, path, self._storage)

    def change_password(self, old_password, new_password):
        if not self.verify_password(old_password, self._master_hash):
            raise PasswordIncorrectError("Старый пароль некорректен!")
        decrypted = self.decrypt_data(old_password, self._storage)
        self._master_hash = self.hash_password(new_password)
        encrypted = self.encrypt_data(new_password, decrypted)
        self.save_storage(new_password, self._pass_path, encrypted)

    def change_path(self, password, path):
        if not self.verify_password(password, self._master_hash):
            raise PasswordIncorrectError("Пароль некорректен!")
        self._pass_path = path
        self.load_storage(password, path)

    def encrypt_data(self, password: str, data):
        if not self.verify_password(password, self._master_hash):
            raise PasswordIncorrectError("Пароль некорректен!")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=self._salt, iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
        fernet = Fernet(key)
        res_json = fernet.encrypt(data.encode()).decode("utf-8")
        return res_json

    def save_storage(self, password, path, encrypted_data):
        if not self.verify_password(password, self._master_hash):
            raise PasswordIncorrectError("Пароль некорректен!")
        try:
            with open(path, "w") as storage:
                salt_b64 = base64.urlsafe_b64encode(self._salt).decode("utf-8")
                hash_b64 = base64.urlsafe_b64encode(self._master_hash.encode()).decode(
                    "utf-8"
                )
                full = f"{hash_b64}|{salt_b64}|{encrypted_data}"
                storage.write(full)
        except Exception as e:
            raise InitializationError(str(e))

    def load_storage(self, password, path):
        try:
            with open(path) as storage:
                content = storage.read().strip()
                parts = content.split("|")
                if len(parts) != 3:
                    raise InitializationError("Неверный формат файла!")
                hash_b64, salt_b64, str_data = parts
                self._master_hash = base64.urlsafe_b64decode(hash_b64.encode()).decode()
                self._salt = base64.urlsafe_b64decode(salt_b64.encode())

                if not self.verify_password(password, self._master_hash):
                    raise PasswordIncorrectError("Пароль некорректен!")

                self._storage = str_data

        except PasswordIncorrectError:
            raise PasswordIncorrectError("Пароль некорректен!")
        except Exception as e:
            raise InitializationError(str(e))

    def hash_password(self, password: str) -> str:
        return pbkdf2_sha256.hash(password)

    def verify_password(self, input_password: str, stored_hash: str) -> bool:
        return pbkdf2_sha256.verify(input_password, stored_hash)

    def decrypt_data(self, password, data):
        if not self.verify_password(password, self._master_hash):
            raise PasswordIncorrectError("Пароль некорректен!")
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=self._salt, iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
        fernet = Fernet(key)
        res_json = fernet.decrypt(data.encode()).decode("utf-8")
        return res_json

    def to_json(self, data) -> str:
        try:
            return json.dumps(data, ensure_ascii=False, indent=2)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Ошибка сериализации: {e}") from e

    def add_to_storage(
        self, master_password, place, name, password, link=None, notes=None
    ):
        if not self.verify_password(master_password, self._master_hash):
            raise PasswordIncorrectError("Пароль некорректен!")
        try:
            decrypted = json.loads(self.decrypt_data(master_password, self._storage))
        except Exception:
            decrypted = {}
        decrypted[str(place)] = {"name": name, "password": password}
        if link:
            decrypted[str(place)]["link"] = link
        if notes:
            decrypted[str(place)]["notes"] = notes
        data = self.to_json(decrypted)
        self._storage = self.encrypt_data(master_password, data)
        self.save_storage(master_password, self._pass_path, self._storage)

    def delete_from_storage(self, master_password, place):
        if not self.verify_password(master_password, self._master_hash):
            raise PasswordIncorrectError("Пароль некорректен!")
        try:
            decrypted = json.loads(self.decrypt_data(master_password, self._storage))
        except Exception:
            decrypted = {}
        if place in decrypted:
            del decrypted[place]
        data = self.to_json(decrypted)
        self._storage = self.encrypt_data(master_password, data)
        self.save_storage(master_password, self._pass_path, self._storage)

    def get_storage(self, master_password):
        if not self.verify_password(master_password, self._master_hash):
            raise PasswordIncorrectError("Старый пароль некорректен")
        try:
            decrypted = json.loads(self.decrypt_data(master_password, self._storage))
        except Exception:
            decrypted = {}
        return decrypted
