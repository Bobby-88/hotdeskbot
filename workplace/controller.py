from typing import List, Set, Union
import logging
from datetime import datetime

from user.credentials import User, UserDB
from workplace.pool import Workplace, WorkplacePool, WorkplaceRequest, WP_TYPE_HOTDESK, WP_TYPE_ASSIGNED
from workplace.reservation import Reservation, ReservationPool, SOMETIMES_IN_THE_PAST, SOMETIMES_IN_THE_FUTURE

QUARANTINE_EASING_START = datetime(2020, 6, 1) # Can work but keep distance
QUARANTINE_EASING_END   = datetime(2020, 7, 1) # Can or with no restrictions
QUARANTINE_DISTANCE = 2 # Minimum allowed distance between workplaces

users = UserDB()
users.Load()

wp_pool = WorkplacePool()
wp_pool.Load()

reservations = ReservationPool()
reservations.Load()

def get_uid_by_tgid(tg_id: str) -> str:
    global users
    user = users.get_user_by_tgid(tg_id)
    return user["email"]



# def get_workplace_by_user(user_id: str) -> str:
#     pass
#
# def is_workplace_safe(workplace_id: str) -> bool:
#     return True
#
# def get_safe_workplace() -> str:
#     safe_workplace_id = ''
#     return safe_workplace_id
#
# def get_workplace(workplace_options: list) -> str:
#     workplace_id = ''
#     return workplace_id
#
# def reserve_workplace(workplace_id: str):
#     pass
#
# def workplaces_are_available() -> bool:
#     return True
#
# def user_has_reserved_workplace(user_id: str) -> bool:
#     return False

################################################################################
# For INTERNAL use - do not export/import this
def get_availabile_wp(from_date: datetime, to_date: datetime, criteria: WorkplaceRequest, min_distance = 0) -> Union[WorkplacePool, None]:
    ### What is already occupied for the dates
    existing_reservations = reservations.get_reservations(from_date, to_date)
    logging.debug("Existing reservations for the dates:\n{}".format(existing_reservations))

    occupied_wp_ids = set()
    for k, v in existing_reservations.items():
        occupied_wp_ids.add(v["workplace"])

    occupied_wp_ids = list(occupied_wp_ids)
    occupied_wp_ids.sort()
    logging.info("Occupied workplaces for the dates: {}".format( occupied_wp_ids ))

    ### Unoccupied places matching criteria
    req = criteria

    if "excluded_ids" not in req or type(req["excluded_ids"]) != list:
        req["excluded_ids"] = []

    # Add occupied workplaces to the exception list
    req["excluded_ids"] = list(set().union(req["excluded_ids"], occupied_wp_ids))

    logging.info("Unoccupied workplace request: {}".format(req) )

    available_wp = wp_pool.get_workplaces(req)
    logging.info("Unoccupied workplaces matching criteria:\n{}".format(available_wp) )

    ### Distance check
    if min_distance > 0:
        logging.info("Distance validation against: {}".format( occupied_wp_ids ))

        unsafe_wp_keys = set()
        for awp_k, awp_v in available_wp.items():
            is_safe = True
            logging.debug("WP: {}".format(awp_k))
            for owp_k in occupied_wp_ids:
                if awp_k == owp_k:
                    continue

                if owp_k not in wp_pool: # Error: there is reservation, there is no worplace in the pool
                    continue

                owp_v = wp_pool[owp_k]

                distance = awp_v.get_distance(owp_v)

                logging.debug(">> {}({},{}) - {}({},{}) = {}".format(
                    awp_k, awp_v["coord_x"], awp_v["coord_y"],
                    owp_k, owp_v["coord_x"], owp_v["coord_y"],
                    distance))

                if distance < QUARANTINE_DISTANCE:
                    logging.info("WP unsafe: {}({},{}) - {}({},{}) = {} < {}".format(
                        awp_k, awp_v["coord_x"], awp_v["coord_y"],
                        owp_k, owp_v["coord_x"], owp_v["coord_y"],
                        distance, QUARANTINE_DISTANCE))

                    is_safe = False
                    unsafe_wp_keys.add(awp_k)
                    break

            if is_safe:
                logging.info("WP SAFE: {}({},{})".format(
                    awp_k, awp_v["coord_x"], awp_v["coord_y"])
                )

        for k in unsafe_wp_keys:
            del available_wp[k]

    ### Summary
    logging.info("Workplaces available to the user:\n{}".format(available_wp) )

    if len(available_wp) == 0:
        logging.info("No place to reserve")
        return None

    return available_wp

# For external use
def release_wp(user_id: str, from_date: datetime, to_date: datetime) -> None:
    pass

# For external use
def reserve_quarantine_wp(user_id: str) -> Union[Workplace, None]:
    from_date = QUARANTINE_EASING_START
    to_date =  QUARANTINE_EASING_END

    user = users.get_user(user_id)
    logging.debug("User:\n{}".format(user))
    # office = "Kyiv"
    office = user["office"]

    criteria = WorkplaceRequest(
        {
            "type": [WP_TYPE_HOTDESK, WP_TYPE_ASSIGNED],
            "office": [ office ]
        }
    )

    # No user preferences

    available_wp = get_availabile_wp(from_date, to_date, criteria, QUARANTINE_DISTANCE)

    if available_wp is None:
        return None

    # Choosing specific place
    wp_to_reserve_key = None

    wp_key = user["owned_wp"]
    if wp_key != "":
        if wp_key in available_wp:
            logging.info("User assigned workplace WILL BE USED: '{}'".format(wp_key))
            wp_to_reserve_key = wp_key
        else:
            logging.info("User assigned workplace occupied/UNSAFE: '{}'".format(wp_key))
    else:
        logging.info("User has NO assigned workplace")

    if wp_to_reserve_key is None:
        wp_to_reserve_key = list(available_wp.keys())[0]

    wp_to_reserve = available_wp[ wp_to_reserve_key ]
    logging.info("Workplace to reserve:\n'{}': {}".format(wp_to_reserve_key, wp_to_reserve) )

    res = Reservation( {
        "workplace": wp_to_reserve_key,
        "user": user_id,
        "reserved_from": from_date,
        "reserved_to": to_date,
        "name": ""
    } )
    logging.info("Adding reservation:\n{}".format(res))
    reservations.set_reservation(res)
    logging.info("Reservation completed")

    return wp_to_reserve

# For external use
def reserve_hotdesk(user_id: str, office: str, from_date: datetime, to_date: datetime) -> Union[Workplace, None]:
    user = users.get_user(user_id)

    criteria = WorkplaceRequest(
        {
            "type": [WP_TYPE_HOTDESK] ,
            "office": [ office ]
        }
    )

    logging.info("User preferencs: {}".format(user["preferences"]) )
    criteria.update(user["preferences"])

    available_wp = get_availabile_wp(from_date, to_date, criteria)

    if available_wp is None:
        return None

    # Choosing specific place
    wp_to_reserve_key = list(available_wp.keys())[0]
    wp_to_reserve = available_wp[ wp_to_reserve_key ]
    logging.info("Workplace to reserve:\n'{}': {}".format(wp_to_reserve_key, wp_to_reserve) )

    res = Reservation( {
        "workplace": wp_to_reserve_key,
        "user": user_id,
        "reserved_from": from_date,
        "reserved_to": to_date,
        "name": ""
    } )
    logging.info("Adding reservation:\n{}".format(res))
    reservations.set_reservation(res)
    logging.info("Reservation is completed".format(res))

    return wp_to_reserve

################################################################################

def test() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: ('%(module)s', %(lineno)d) %(message)s")

    # reserve_hotdesk('kroz.nn@gmail.com', 'Kyiv', datetime(2020, 6, 1), datetime(2020, 6, 20))

    reserve_quarantine_wp('kroz.nn@gmail.com')


if __name__ == '__main__':
    test()
