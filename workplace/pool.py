from typing import List, Set, Union # https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
import logging
import math

from storage import gsheet

# TODO: Consideration of constraints

WP_TYPE_HOTDESK = "hotdesk"
WP_TYPE_ASSIGNED = "assigned"
FAR_AWAY = 99999

class WorkplaceRequest(dict):
    def __init__(self, data):
        if not self.is_valid(data):
            logging.error("Invalid workspace request: {}".format(data))

        super().__init__(data)

    @staticmethod
    def is_valid(data: Union[dict, 'WorkplaceRequest']) -> bool:
        # Distance is int; others - list
        valid_fields = {"distance", "excluded_ids", "office", "floor", "number", "type", "options", "constraints", "coord_x", "coord_y"}
        data_fields = set(data.keys())
        if not data_fields.issubset(valid_fields):
            logging.info("Invalid fields: {} <-> {}".format(data_fields, valid_fields))
            return False

        list_fields = {"excluded_ids", "office", "floor", "number", "type", "options", "constraints", "coord_x", "coord_y"}
        for k in list_fields:
            if k in data:
                v = data[k]
                if type(v) is not list:
                    logging.info("Invalid field type: data['{}']: {}".format(k, type(v)))
                    return False

        int_fields = {"distance"}
        for k in int_fields:
            if k in data:
                v = data[k]
                if type(v) is not int:
                    logging.info("Invalid field type: data['{}']: {}".format(k, type(v)))
                    return False

        if "type" in data.keys() and any(t not in {WP_TYPE_HOTDESK, WP_TYPE_ASSIGNED} for t in data['type']):
            logging.info("Invalid type: {}".format(data['type']))
            return False

        return True

class Workplace(dict):
    def __init__(self, data):
        if not self.is_valid(data):
            logging.error("Invalid workspace: {}".format(data))

        super().__init__(data)

    @staticmethod
    def is_valid(data: Union[dict, 'Workplace']) -> bool:
        valid_fields = {"office", "floor", "number", "type", "options", "constraints", "coord_x", "coord_y"}
        data_fields = set(data.keys())
        if not data_fields.issubset(valid_fields):
            logging.info("Invalid fields: {} <-> {}".format(data_fields, valid_fields))
            return False

        mandatory_fields = {"office", "floor", "number", "type", "options", "constraints", "coord_x", "coord_y"}
        data_fields = set(data.keys())
        if not mandatory_fields.issubset(data_fields):
            logging.info("No manadatory fields: {} <-> {}".format(data_fields, valid_fields))
            return False

        if data['type'] not in {WP_TYPE_HOTDESK, WP_TYPE_ASSIGNED}:
            logging.info("Invalid type: {}".format(data['type']))
            return False

        return True


    def matches(self, request: WorkplaceRequest) -> bool:
        logging.debug("Matching {}".format(self))
        for c in list(request.keys()):
            logging.debug(">> Criteria: '{}'".format(c))
            if c in self:
                s_value_list = self[c]
                if type(s_value_list) != list:
                    s_value_list= [s_value_list]

                criteria_match = False
                for r_v in request[c]:

                    subcriteria_value_list = r_v.split(',')
                    logging.debug(">> Request value: '{}' -> {}".format(r_v, subcriteria_value_list))

                    subcriteria_match = True
                    for s_r_v in subcriteria_value_list:
                        subcriteria_match = subcriteria_match and any(s_v == s_r_v for s_v in s_value_list)
                    criteria_match = criteria_match or subcriteria_match

                if not criteria_match:
                    logging.debug(">> Does NOT comply criteria '{}': (seat) '{}' != (request) '{}'".format(c, self[c], request[c]))
                    return False

        logging.debug(">> COMPLIES")
        return True

    def get_distance(self, pair: 'Workplace'):
        if self['office'] != pair['office'] or self['floor'] != pair ['floor']:
            return FAR_AWAY

        return math.sqrt( math.pow(self['coord_x'] - pair['coord_x'], 2) + math.pow(self['coord_y'] - pair['coord_y'], 2) )

class WorkplacePool(dict):
    def __init__(self, data = {}):
        super().__init__(data)

    def __str__(self):
        r = ""
        for k, v in self.items():
            if r != "":
                r = r + "\n"
            r = r + "{}: {}".format(k, v)
        return r

    def get_workplaces(self, request: Union[dict, WorkplaceRequest] = {}) -> 'WorkplacePool':
        if type(request) is not WorkplaceRequest:
            request = WorkplaceRequest(request)

        exclided_ids = []
        if "excluded_ids" in request:
            exclided_ids = request["excluded_ids"]

        r = WorkplacePool()
        for k, v in self.items():
            if k in exclided_ids:
                continue
            # This will not consider distance
            if v.matches(request):
                r[k] = v

        # Consideration of distance
        if 'distance' in request:
            keys = list(r.keys())
            i = 0
            while i<len(keys):
                k_i = keys[i]
                j = i + 1
                while j<len(keys):
                    k_j = keys[j]
                    if self[k_i].get_distance(self[k_j]) < request['distance']:
                        # keys.pop(j)
                        del keys[j]
                        del r[k_j]
                        j = j - 1
                    j = j + 1
                i = i + 1

        return r

    def __get_unique_values(self, request: Union[dict, WorkplaceRequest], field: str) -> Set[str]:
        r = set()
        for k, v in self.items():
            if v.matches(request):
                r.add(v[field])

        return r

    def get_offices(self, request: Union[dict, WorkplaceRequest] = {}) -> Set[str]:
        return self.__get_unique_values(request, "office")

    def get_floors(self, request: Union[dict, WorkplaceRequest] = {}) -> Set[str]:
        return self.__get_unique_values(request, "floor")

    def Load(self) -> None:
        gsheet.open()
        for row in gsheet.get_workspaces():
            if len(row) != 9:
                logging.error("Invalid record: {}", row)
                continue

            wp_id = row[0]
            data = {
                "office": row[1],
                "floor": row[2],
                "number": row[3],
                 "type": row[4],
                 "options": row[5].split(","),
                 "constraints": row[6].split(","),
                 "coord_x": row[7],
                 "coord_y": row[8]
            }

            self[wp_id] = Workplace(data)

    # For testing needs only
    def LoadTest(self) -> None:
        logging.warning("Loading test data")
        self["Kiev-HD-01"] = Workplace( { "office": "Kiev",   "floor": "6", "number": "505-01", "type": WP_TYPE_HOTDESK,  "options": ["window", "printer"             ], "constraints": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-02"] = Workplace( { "office": "Kiev",   "floor": "5", "number": "505-02", "type": WP_TYPE_HOTDESK,  "options": ["window", "printer", "project_x"], "constraints": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-03"] = Workplace( { "office": "Moscow", "floor": "5", "number": "505-03", "type": WP_TYPE_HOTDESK,  "options": ["window",                       ], "constraints": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-04"] = Workplace( { "office": "Moscow", "floor": "5", "number": "505-04", "type": WP_TYPE_ASSIGNED, "options": ["window",            "project_x"], "constraints": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-05"] = Workplace( { "office": "Moscow", "floor": "4", "number": "505-05", "type": WP_TYPE_ASSIGNED, "options": [          "printer"             ], "constraints": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-06"] = Workplace( { "office": "Moscow", "floor": "4", "number": "505-06", "type": WP_TYPE_HOTDESK,  "options": [          "printer", "project_x"], "constraints": [], "coord_x": 1, "coord_y": 2 } )

        self["Kiev-HD-07"] = Workplace( { "office": "Kiev",   "floor": "3", "number": "505-07", "type": WP_TYPE_HOTDESK,  "options": [                                ], "constraints": [], "coord_x": 1, "coord_y": 1 } )
        self["Kiev-HD-08"] = Workplace( { "office": "Kiev",   "floor": "3", "number": "505-08", "type": WP_TYPE_ASSIGNED, "options": [                     "project_x"], "constraints": [], "coord_x": 2, "coord_y": 1 } )
        self["Kiev-HD-09"] = Workplace( { "office": "Kiev",   "floor": "3", "number": "505-09", "type": WP_TYPE_ASSIGNED, "options": [                                ], "constraints": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-10"] = Workplace( { "office": "Kiev",   "floor": "3", "number": "505-10", "type": WP_TYPE_ASSIGNED, "options": [                                ], "constraints": [], "coord_x": 2, "coord_y": 2 } )
        self["Kiev-HD-11"] = Workplace( { "office": "Kiev",   "floor": "3", "number": "505-10", "type": WP_TYPE_ASSIGNED, "options": [                     "project_x"], "constraints": [], "coord_x": 1, "coord_y": 3 } )

################################################################################

def test() -> None:
    # CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET - https://docs.python.org/3/library/logging.html#logging-levels
    # logging.basicConfig(level=logging.NOTSET, format="%(levelname)s: ('%(module)s', %(lineno)d) %(message)s")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: ('%(module)s', %(lineno)d) %(message)s")

    pool = WorkplacePool()
    pool.Load()

    print("== Whole pool:")
    print(pool)

    print()
    print("== Selections:")
    print("Offices: {}".format(pool.get_offices()))
    print("Floors: {}".format(pool.get_floors()))

    print()
    print("== Query result:")
    # options = pool.get_workplaces({"type": [WP_TYPE_HOTDESK] })
    options = pool.get_workplaces({"excluded_ids": ["Kiev-HD-01", "Kiev-HD-03"], "type": [WP_TYPE_HOTDESK] })
    # options = pool.get_workplaces({"floor": ["9", "5"] })
    # options = pool.get_workplaces({"type": [WP_TYPE_HOTDESK], "floor": ["4", "5"] })
    # options = pool.get_workplaces({"options":["window,project_x"]})
    # options = pool.get_workplaces({"distance": 2, "floor": ["3"] })
    # options = pool.get_workplaces({"distance": 3, "floor": ["3"], "options":["project_x"] })
    # options = pool.get_workplaces({"distance": 2, "floor": ["3"], "options":["project_x"] })
    print(options)


###


if __name__ == '__main__':
    test()

