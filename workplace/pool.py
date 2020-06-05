from typing import List, Set, Union # https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
import logging

WP_TYPE_HOTDESK = "hotdesk"
WP_TYPE_ASSIGNED = "assigned"

# TODO: Coronavirus case

class WorkplaceRequest(dict):
    def __init__(self, data):
        if not self.is_valid(data):
            logging.error("Invalid workspace: {}".format(data))

        super().__init__(data)

    @staticmethod
    def is_valid(data: Union[dict, 'WorkplaceRequest']) -> bool:
        valid_fields = {"office", "floor", "number", "type", "options", "constraints", "coord_x", "coord_y"}
        data_fields = set(data.keys())
        if not data_fields.issubset(valid_fields):
            logging.debug("Invalid fields: {} <-> {}".format(data_fields, valid_fields))
            return False

        if "type" in data.keys() and any(t not in {WP_TYPE_HOTDESK, WP_TYPE_ASSIGNED} for t in data['type']):
            logging.debug("Invalid type: {}".format(data['type']))
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
            logging.debug("Invalid fields: {} <-> {}".format(data_fields, valid_fields))
            return False

        mandatory_fields = {"office", "floor", "number", "type", "options", "constraints", "coord_x", "coord_y"}
        data_fields = set(data.keys())
        if not mandatory_fields.issubset(data_fields):
            logging.debug("No manadatory fields: {} <-> {}".format(data_fields, valid_fields))
            return False

        if data['type'] not in {WP_TYPE_HOTDESK, WP_TYPE_ASSIGNED}:
            logging.debug("Invalid type: {}".format(data['type']))
            return False

        return True


    def matches(self, request: WorkplaceRequest) -> bool:
        if type(request) is not WorkplaceRequest:
            request = WorkplaceRequest(request)

        logging.debug("Matching {}".format(self))
        for c in list(request.keys()):
            logging.debug(">> Criteria: '{}'".format(c))
            if c in self:
                s_value_list = self[c]
                if type(s_value_list) != list:
                    s_value_list= [s_value_list]

                criteria_match = False
                for r_v in request[c]:

                    # criteria_match = criteria_match or any(s_v == r_v for s_v in s_value_list)
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
        r = WorkplacePool()
        for k, v in self.items():
            if v.matches(request):
                r[k] = v

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

    # For testing needs only
    def LoadTest(self) -> None:
        logging.warning("Loading test data")
        self["Kiev-HD-1"] = Workplace( { "office": "Kiev",   "floor": "6", "number": "505-1", "type": WP_TYPE_HOTDESK,  "options": ["window", "printer"             ], "constraints": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-2"] = Workplace( { "office": "Kiev",   "floor": "5", "number": "505-2", "type": WP_TYPE_HOTDESK,  "options": ["window", "printer", "project_x"], "constraints": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-3"] = Workplace( { "office": "Moscow", "floor": "5", "number": "505-3", "type": WP_TYPE_HOTDESK,  "options": ["window",                       ], "constraints": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-4"] = Workplace( { "office": "Moscow", "floor": "5", "number": "505-4", "type": WP_TYPE_ASSIGNED, "options": ["window",            "project_x"], "constraints": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-5"] = Workplace( { "office": "Moscow", "floor": "4", "number": "505-5", "type": WP_TYPE_ASSIGNED, "options": [          "printer"             ], "constraints": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-6"] = Workplace( { "office": "Moscow", "floor": "4", "number": "505-6", "type": WP_TYPE_HOTDESK,  "options": [          "printer", "project_x"], "constraints": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-7"] = Workplace( { "office": "Kiev",   "floor": "4", "number": "505-7", "type": WP_TYPE_HOTDESK,  "options": [                     "project_x"], "constraints": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-8"] = Workplace( { "office": "Kiev",   "floor": "4", "number": "505-8", "type": WP_TYPE_ASSIGNED, "options": [                                ], "constraints": [], "coord_x": 1, "coord_y": 2 } )

# TODO
def get_seat():
    pass

# TODO
def make_greeting_message() -> str:
    # CSS
    pass

# TODO
def make_result_message() -> str:
    pass

def test() -> None:
    # CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET - https://docs.python.org/3/library/logging.html#logging-levels
    # logging.basicConfig(level=logging.NOTSET, format="%(levelname)s: ('%(module)s', %(lineno)d) %(message)s")
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: ('%(module)s', %(lineno)d) %(message)s")

    pool = WorkplacePool()
    pool.LoadTest()

    print("== Whole pool:")
    print(pool)

    print()
    print("== Selections:")
    print("Offices: {}".format(pool.get_offices()))
    print("Floors: {}".format(pool.get_floors()))

    print()
    print("== Query result:")
    # options = pool.get_workplaces({"type": ["hotseat"] })
    # options = pool.get_workplaces({"floor": ["9", "5"] })
    options = pool.get_workplaces({"type": [WP_TYPE_HOTDESK], "floor": ["4", "5"] })
    # options = pool.get_workplaces({"options":["window,project_x"]})
    print(options)


###


if __name__ == '__main__':
    test()

