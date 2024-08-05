import json
import os
import pathlib
from django.core.management.base import BaseCommand, CommandError
from Crypto.Cipher import AES


def decrypt_user_id(user_id: str) -> str:
    data_encryption_key = os.getenv("MAGNIX_DATA_ENCRYPTION_KEY")
    cipher = AES.new(data_encryption_key.encode('utf8'), AES.MODE_ECB)
    return cipher.decrypt(bytes().fromhex(user_id)).decode().strip()


class Command(BaseCommand):
    help = 'Decrypt user id list'

    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str)

    def handle(self, *args, **kwargs):
        file_name = kwargs["file_name"]

        if not os.path.exists(file_name):
            raise CommandError(f" File {file_name} does not exist.")

        file_path = pathlib.Path(file_name)

        with open(file=file_path, mode="r") as ids_file:
            id_list = json.loads(ids_file.read())

        result = []
        for item in id_list:
            try:
                result.append(decrypt_user_id(item.get('user_id')))
            except Exception:
                pass

        with open(file=file_path.parent / f"{file_path.name}_decrypted.txt", mode="w") as output_file:
            output_file.write(
                '\r\n'.join(result)
            )

        self.stdout.write(self.style.WARNING(f"Decrypting {len(id_list) - len(result)} user ids had errors."))
        self.stdout.write(self.style.SUCCESS(f"Successfully decrypted {len(result)} user ids."))
