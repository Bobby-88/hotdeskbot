from workplace.pool import WorkplacePool, Workplace, WorkplaceRequest

pool = WorkplacePool()
pool.LoadTest()

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
