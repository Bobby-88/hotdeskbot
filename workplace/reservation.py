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

    def if_reserved(self, date_from: datetime = None, date_to: datetime = None, user: str = None) -> bool:
        logging.debug("Check if reserved from {} to {} for '{}': {}".format(date_from, date_to, user, self))

        if date_from is None:
            date_from = datetime(1, 1, 1)

        if date_to is None:
            date_from = datetime(9999, 12, 31)

        if date_from > self["reserved_to"]:
            logging.debug(">> NOT reserved: date_from > reserved_to")
            return False

        if date_to < self["reserved_from"]:
            logging.debug(">> NOT reserved: date_to < reserved_from")
            return False

        if user is not None and user != self["user"]:
            logging.debug(">> NOT reserved: user does not match")
            return False

        logging.debug(">> RESERVED")

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
            res_id = data["workplace"] + ":" + data["user"]

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

    def get_reservations(self, date_from: datetime, date_to: datetime, user = None) -> 'ReservationPool':
        r = ReservationPool()

        for k, v in self.items():
            if v.if_reserved(date_from, date_to, user):
                r[k] = v

        return r

    # TODO: consider dublication case
    def set_reservation(self, reservation: Reservation):
        res_id = reservation["workplace"] + ":" + reservation["user"]

        self[res_id] = Reservation(reservation)

        # ((reservation["reserved_from"], '%m/%d/%Y').days - datetime.datetime(1899, 12, 30).days),
        gsheet_start_days = datetime(1899, 12, 30).date()
        from_days = reservation["reserved_from"].date()
        data = [
            reservation["workplace"],
            reservation["user"],
            (reservation["reserved_from"].date() - gsheet_start_days).days,
            (reservation["reserved_to"].date()   - gsheet_start_days).days,
            reservation["name"],
        ]

        gsheet.add_reservation(data)


################################################################################

def test() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: ('%(module)s', %(lineno)d) %(message)s")

    pool = ReservationPool()
    pool.Load()

    print("== Whole pool:")
    print(pool)
    print()

    print("== Special query:")
    print( pool.get_reservations(datetime(2020, 6, 1), datetime(2020, 6, 20)) )

    print()
    print("== Query by user:")
    print( pool.get_reservations(datetime(2020, 4, 1), datetime(2020,4, 2)) )
    print()
    print( pool.get_reservations(datetime(2020, 4, 1), datetime(2020,4, 10)) )
    print()
    print( pool.get_reservations(datetime(2020, 4, 1), datetime(2020,4, 10), "vi2@gmail" ))

    print()
    res = Reservation( {
        "workplace": "seat123",
        "user": "user1",
        "reserved_from": datetime(2020, 6, 1),
        "reserved_to": datetime(2020,6,5),
        "name": "Name"
    } )
    # print("Adding reservation: {}".format(res))
    # pool.set_reservation(res)


if __name__ == '__main__':
    test()
