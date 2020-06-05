from typing import List, Set

from user.credentials import *

# TODO: static -> assigned
# TODO: const static/hotseat
# TODO: const workplace features
# TODO: Coronavirus case

class WorkplaceRequest(dict):
    def __init__(self, data):
        super().__init__(data)

class Workplace(dict):
    def __init__(self, data):
        super().__init__(data)

    def matches(self, request: WorkplaceRequest) -> bool:

        # print()
        # print("DEBUG: {}".format(self))
        for c in list(request.keys()):
            # print("DEBUG: >> Criteria: '{}'".format(c))
            if c in self:
                # for r_v in request[c]:
                #     s_v = self[c]
                #     if s_v != r_v:
                #         print("DEBUG: Not matching criteria '{}': Seat:'{}' != Request:'{}'".format(c, s_v, r_v))
                #         return False

                s_value_list = self[c]
                if type(s_value_list) != list:
                    s_value_list= [s_value_list]

                criteria_match = False
                for r_v in request[c]:

                    # criteria_match = criteria_match or any(s_v == r_v for s_v in s_value_list)
                    subcriteria_value_list = r_v.split(',')
                    # print("DEBUG: >> Request value: '{}' -> {}".format(r_v, subcriteria_value_list))

                    subcriteria_match = True
                    for s_r_v in subcriteria_value_list:
                        subcriteria_match = subcriteria_match and any(s_v == s_r_v for s_v in s_value_list)
                    criteria_match = criteria_match or subcriteria_match

                if not criteria_match:
                    # print("DEBUG: Not matching criteria '{}': (seat) '{}' != (request) '{}'".format(c, self[c], request[c]))
                    return False

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

    def get_workplaces(self, request):
        r = WorkplacePool()
        for k, v in self.items():
            if v.matches(request):
                r[k] = v

        return r

    def __get_unique_values(self, request, field: str) -> Set[str]:
        r = set()
        for k, v in self.items():
            if v.matches(request):
                r.add(v[field])

        return r

    def get_offices(self, request = {}) -> Set[str]:
        return self.__get_unique_values(request, "office")

    def get_floors(self, request = {}) -> Set[str]:
        return self.__get_unique_values(request, "floor")

    # For testing needs only
    def LoadTest(self):
        self["Kiev-HD-1"] = Workplace( { "office": "Kiev", "floor": "6", "number": "505-1", "type": "hotseat", "options": ["window", "printer"             ], "req": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-2"] = Workplace( { "office": "Kiev", "floor": "5", "number": "505-2", "type": "hotseat", "options": ["window", "printer", "project_x"], "req": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-3"] = Workplace( { "office": "Moscow", "floor": "5", "number": "505-3", "type": "hotseat", "options": ["window",                       ], "req": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-4"] = Workplace( { "office": "Moscow", "floor": "5", "number": "505-4", "type": "static",  "options": ["window",            "project_x"], "req": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-5"] = Workplace( { "office": "Moscow", "floor": "4", "number": "505-5", "type": "static",  "options": [          "printer"             ], "req": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-6"] = Workplace( { "office": "Moscow", "floor": "4", "number": "505-6", "type": "hotseat", "options": [          "printer", "project_x"], "req": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-7"] = Workplace( { "office": "Kiev", "floor": "4", "number": "505-7", "type": "hotseat", "options": [                     "project_x"], "req": [], "coord_x": 1, "coord_y": 2 } )
        self["Kiev-HD-8"] = Workplace( { "office": "Kiev", "floor": "4", "number": "505-8", "type": "static",  "options": [                                ], "req": [], "coord_x": 1, "coord_y": 2 } )

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

def test():
    pool = WorkplacePool()
    pool.LoadTest()

    print(pool)
    print("---------")
    print("Offices: {}".format(pool.get_offices()))
    print("Floors: {}".format(pool.get_floors()))
    print("---------")
    # options = pool.get_workplaces({"type": ["hotseat"] })
    # options = pool.get_workplaces({"floor": ["9", "5"] })
    # options = pool.get_workplaces({"type": ["static"], "floor": ["4", "5"] })
    options = pool.get_workplaces({"options":["window,project_x"]})
    print(options)


###


if __name__ == '__main__':
    test()

