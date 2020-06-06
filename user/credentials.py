from typing import List, Set, Union # https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
import logging
from datetime import datetime, date
import json

from storage import gsheet

class User(dict):
    def __init__(self, data):
        if not self.is_valid(data):
            logging.error("Invalid user record: {}".format(data))

        super().__init__(data)

    @staticmethod
    def is_valid(data: Union[dict, 'User']) -> bool:
        valid_fields = {"email", "password", "office", "tg_id", "name", "preferences", "owned_wp"}
        data_fields = set(data.keys())
        if not data_fields.issubset(valid_fields):
            logging.info("Invalid fields: {} <-> {}".format(data_fields, valid_fields))
            return False

        mandatory_fields = {"email", "office", "name"}
        data_fields = set(data.keys())
        if not mandatory_fields.issubset(data_fields):
            logging.info("No manadatory fields: {} <-> {}".format(data_fields, valid_fields))
            return False

        return True


class UserDB(dict):
    def __init__(self, data = {}):
        super().__init__(data)

    def __str__(self):
        r = ""
        for k, v in self.items():
            if r != "":
                r = r + "\n"
            r = r + "'{}': {}".format(k, v)
        return r

    def Load(self) -> None:
        gsheet.open()
        for row in gsheet.get_users():
            if len(row) != 7:
                logging.error("Invalid record: {}", row)
                continue

            data = {
                "email": row[0],
                "password": row[1],
                "office": row[2],
                "tg_id": row[3],
                "name": row[4],
                "preferences": row[5],
                "owned_wp": row[6]
            }
            user_id = data["email"]

            if data["preferences"] == "":
                data["preferences"] = {}
            else:
                data["preferences"] = json.loads(data["preferences"])

            self[user_id] = User(data)

    def get_user(self, email: str) -> User:
        return self[email]

    def get_user_by_tgid(self, tg_id: str) -> User:
        for k, v in self.items():
            if v["tg_id"] == tg_id:
                return v

        return None


################################################################################

def test() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: ('%(module)s', %(lineno)d) %(message)s")

    pool = UserDB()
    pool.Load()

    print("== Whole pool:")
    print(pool)

    print()
    print("== Query by id:")
    print( pool.get_user("vi@gmail.com"))

    print()
    print("== Query by Telegram Id:")
    print( pool.get_user_by_tgid("412037304") )

if __name__ == '__main__':
    test()
