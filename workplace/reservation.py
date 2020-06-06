from typing import List, Set, Union # https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
import logging
from datetime import datetime, date

from storage import gsheet

# TODO: all queries shall be linked to specfic office: user is allowed to occupy several places in differen offices
# TODO: what if user partially occupies the place. Suggestion: update existing record.


class Reservation(dict):
    def __init__(self, data):
        if not self.is_valid(data):
            logging.error("Invalid workspace: {}".format(data))

        super().__init__(data)

    @staticmethod
    def is_valid(data: Union[dict, 'Reservation']) -> bool:
        valid_fields = {"workplace", "user", "reserved_from", "reserved_to", "name"}
        data_fields = set(data.keys())
        if not data_fields.issubset(valid_fields):
            logging.info("Invalid fields: {} <-> {}".format(data_fields, valid_fields))
            return False

        mandatory_fields = {"workplace", "user", "reserved_from", "name"}
        data_fields = set(data.keys())
        if not mandatory_fields.issubset(data_fields):
            logging.info("No manadatory fields: {} <-> {}".format(data_fields, valid_fields))
            return False

        if type(data["reserved_from"]) is not datetime:
            logging.info("Incorrect type of 'reserved_from': '{}'".format(type(data["reserved_from"])))
            return False

        if type(data["reserved_to"]) is not datetime:
            logging.info("Incorrect type of 'reserved_to".format(type(data["reserved_to"])))
            return False

        if data["reserved_from"] > data["reserved_to"]:
            logging.info("'reserved_from' > 'reserved_to': {} > {}".format( data["reserved_from"], data["reserved_to"]))
            return False

        return True

class ReservationPool(dict):
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
        for row in gsheet.get_reservations():
            if len(row) != 5:
                logging.error("Invalid record: {}", row)
                continue

            data = {
                "workplace": row[0],
                "user": row[1],
                "reserved_from": row[2],
                "reserved_to": row[3],
                "name": row[4]
            }
            res_id = data["workplace"] + ":" + data["user"] + ":" + data["reserved_from"] + ":" + data["reserved_to"]

            if data["reserved_from"] != "":
                data["reserved_from"] = datetime.strptime(data["reserved_from"], '%m/%d/%Y')
            else:
                data["reserved_from"] = datetime(1, 1, 1)

                # datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
            if data["reserved_to"] != "":
                data["reserved_to"] = datetime.strptime(data["reserved_to"], '%m/%d/%Y')
            else:
                data["reserved_to"] = datetime(9999, 12, 31)

            self[res_id] = Reservation(data)

    def if_reserved_to_user(self, user: str, date_from: datetime, date_to: datetime) -> bool:
        logging.debug("Check if reserved from {} to {} by '{}'".format(date_from, date_to, user))

        if date_from is None:
            date_from = datetime(1, 1, 1)

        if date_to is None:
            date_from = datetime(9999, 12, 31)

        for k, v in self.items():
            logging.debug(">> Record: {}".format(v))

            if date_from > v["reserved_to"]:
                logging.debug(">> ... date_from skips")
                continue

            if date_to < v["reserved_from"]:
                logging.debug(">> ... date_to skips")
                continue

            if user == v["user"]:
                logging.debug(">> Found!")
                return k

            logging.debug(">> User does not match")

        return None

################################################################################

def test() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: ('%(module)s', %(lineno)d) %(message)s")

    pool = ReservationPool()
    pool.Load()

    print("== Whole pool:")
    print(pool)

    print()
    print("== Query by user:")
    print( pool.if_reserved_to_user("vi2@gmail", datetime(2020, 4, 1), datetime(2020,4, 10)) )
    print( pool.if_reserved_to_user("vi2@gmail", datetime(2020, 4, 1), datetime(2020,4, 2)) )


if __name__ == '__main__':
    test()
