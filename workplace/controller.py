from typing import List, Set, Union
import logging
from datetime import datetime

from user.credentials import UserDB
from workplace.pool import Workplace, WorkplacePool, WorkplaceRequest, WP_TYPE_HOTDESK
from workplace.reservation import Reservation, ReservationPool

users = UserDB()
users.Load()

wp_pool = WorkplacePool()
wp_pool.Load()

reservations = ReservationPool()
reservations.Load()

def get_workplace_by_user(user_id: str) -> str:
    pass

def is_workplace_safe(workplace_id: str) -> bool:
    return True

def get_safe_workplace() -> str:
    safe_workplace_id = ''
    return safe_workplace_id

def get_workplace(workplace_options: list) -> str:
    workplace_id = ''
    return workplace_id

def reserve_workplace(workplace_id: str):
    pass

def workplaces_are_available() -> bool:
    return True

def user_has_reserved_workplace(user_id: str) -> bool:
    return False

################################################################################
# TODO: get preferences from user
def reserve_hotdesk(user_id, office, from_date, to_date) -> Union[Workplace, None]:
    user = users.get_user(user_id)

    reserved_wp = reservations.get_reservations(from_date, to_date)
    logging.info("Existing reservations to the dates:\n{}".format(reserved_wp))

    exception_list = set()
    for k, v in reserved_wp.items():
        exception_list.add(v["workplace"])

    req = WorkplaceRequest(
        {
            "type": [WP_TYPE_HOTDESK] ,
            "office": [ office ],
            "excluded_ids": list(exception_list),
        }
    )

    logging.info("User preferencs: {}".format(user["preferences"]) )
    req.update(user["preferences"])

    logging.info("Workplace request: {}".format(req) )

    # available_wp = wp_pool.get_workplaces({"excluded_ids": list(exception_list), "type": [WP_TYPE_HOTDESK] , "office": ["Kyiv"], "floor": ["3"]})
    available_wp = wp_pool.get_workplaces(req)
    logging.info("Workplaces available to the user:\n{}".format(available_wp) )

    if len(available_wp) == 0:
        logging.info("No place to reserve")
        return None

    wp_to_reserve_key = list(available_wp.keys())[0]
    wp_to_reserve = available_wp[ wp_to_reserve_key ]
    logging.info("Workplace to reserve: {}".format(wp_to_reserve) )

    res = Reservation( {
        "workplace": wp_to_reserve_key,
        "user": user_id,
        "reserved_from": from_date,
        "reserved_to": to_date,
        "name": ""
    } )
    logging.info("Adding reservation: {}".format(res))
    reservations.set_reservation(res)
    logging.info("Reservation is completed".format(res))

    return wp_to_reserve

    # options = wp_pool.get_workplaces({"excluded_ids": ["Kiev-HD-01", "Kiev-HD-03"], "type": [WP_TYPE_HOTDESK] })

def test() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: ('%(module)s', %(lineno)d) %(message)s")

    # old - reserve_hotdesk("know.nn@gmail.com", "Kyiv", datetime(2020, 6, 1), datetime(2020, 6, 20), {"floor": ["3"]})
    reserve_hotdesk('kroz.nn@gmail.com', 'Kyiv', datetime(2020, 6, 1), datetime(2020, 6, 20))


if __name__ == '__main__':
    test()
