from workplace.controller import *

def print_reservation_result(workplace_id: str):
    pass

# Print .md
def print_greeting():
    pass

### Functions which correspond to buttons in bot
# Key use cases

def want_hotdesk(criteria):
    pass

def give_place():
    pass

# Quarantine
def want_to_work(update, context):
    if not workplaces_are_available():
        print('Unfortunately, there are currently no workplaces available.')
        return

    # get user from context
    user_id = ''
    workplace_id = get_workplace_by_user(user_id)

    if user_has_reserved_workplace(user_id):
        print_reservation_result(workplace_id)
        return

    if is_workplace_safe(workplace_id):
        reserve_workplace(workplace_id)
        print_reservation_result(workplace_id)
    else:
        safe_workplace_id = get_safe_workplace()
        print_reservation_result(workplace_id)