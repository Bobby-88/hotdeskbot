from typing import List, Set, Union # https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
import logging
from datetime import datetime, date

from storage import gsheet

class User(dict):
    def __init__(self, data):
        if not self.is_valid(data):
            logging.error("Invalid user record: {}".format(data))

        super().__init__(data)

    @staticmethod
    def is_valid(data: Union[dict, 'Reservation']) -> bool:
        valid_fields = {"email", "password", "office", "tg_id", "name", "preferences"}
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
            if len(row) != 6:
                logging.error("Invalid record: {}", row)
                continue

            data = {
                "email": row[0],
                "password": row[1],
                "office": row[2],
                "tg_id": row[3],
                "name": row[4],
                "preferences": row[5]
            }
            user_id = data["email"]

            self[user_id] = User(data)

    def get_user(self, email: str) -> User:
        return self[email]

################################################################################

def test() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: ('%(module)s', %(lineno)d) %(message)s")

    pool = UserDB()
    pool.Load()

    print("== Whole pool:")
    print(pool)

    print()
    print("== Query user:")
    print( pool.get_user("vi2@gmail.com"))

if __name__ == '__main__':
    test()
