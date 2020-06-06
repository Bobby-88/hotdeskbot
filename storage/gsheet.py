from typing import List
import logging
import gspread
from datetime import datetime

EARLIEST_DATE = datetime(1899, 12, 30) # Date in Google Sheets is a number of days counting from this date

gsheet_name = "Help"

# Tables:
t_users_name = "Credentials" # User id, telegram id, ...
t_reservations_name = "RESERVATIONS" # Who, period
t_workplaces_name = "Workplaces" # Seat id, office-floor-number, features, coordinates
# t_workplaces_name = "Desks" # Seat id, office-floor-number, features, coordinates

gsheet = None
t_users = None
t_reservations = None
t_workplaces = None

def open() -> None:
    global gsheet
    global t_users
    global t_reservations
    global t_workplaces

    if gsheet is None:
        gc = gspread.service_account(filename='gsheet-credentials.json')
        gsheet = gc.open(gsheet_name)
        if gsheet is None:
            raise RuntimeError("Cannot open Google Sheet: '{}'".format(gsheet_name))

    t_users = gsheet.worksheet(t_users_name)
    if t_users is None:
        raise RuntimeError("Cannot open Google Sheet for users: '{}'/'{}'".format(gsheet_name, t_users_name))

    t_reservations = gsheet.worksheet(t_reservations_name)
    if t_reservations is None:
        raise RuntimeError("Cannot open Google Sheet for reservations: '{}'/'{}'".format(gsheet_name, t_reservations_name))

    t_workplaces = gsheet.worksheet(t_workplaces_name)
    if t_workplaces is None:
        raise RuntimeError("Cannot open Google Sheet workplaces: '{}'/'{}'".format(gsheet_name, t_workplaces_name))


def get_users():
    global t_users

    return t_users.get_all_values()[1:]

def get_reservations():
    global t_reservations

    return t_reservations.get_all_values()[1:]

def get_workspaces():
    global t_workplaces

    return t_workplaces.get_all_values()[1:]

def add_reservation(values: List[str]) -> None:
    global t_reservations

    logging.info("Adding line to '{}'/'{}': {}".format(gsheet_name, t_reservations_name, values))
    t_reservations.append_row(values)

################################################################################

def test() -> None:
    open()

    print("== Content of '{}'/'{}' sheet:".format(gsheet_name, t_users_name))
    v = get_users()
    print(v)

    print()
    print("== Content of '{}'/'{}' sheet:".format(gsheet_name, t_reservations_name))
    v = get_reservations()
    print(v)

    print()
    print("== Content of '{}'/'{}' sheet:".format(gsheet_name, t_workplaces_name))
    v = get_workspaces()
    print(v)


# ###########################
#
# def get_offices(sh):
#     offices_worksheet = sh.worksheet("Offices")
#     offices = offices_worksheet.col_values(1)
#     return offices
#
#
# def get_users(sh):
#     credentials_worksheet = sh.worksheet(t_users_name)
#     users = credentials_worksheet.get_all_values()
#     # print(users)
#     return users
#
#
# def persist_user_id(sh, row, id):
#     credentials_worksheet = sh.worksheet(t_users_name)
#     credentials_worksheet.update_cell(row, 4, id)
#     # users = credentials_worksheet.get_all_values()
#     # print(users)
#     return
#
#
# # this gets a list of lists from a gsheet.
# # sheet is an instance of google sheet - this is returned by add_gsheet somewhere in init section
# # worksheet is a sheet name, e.g. "RESERVATIONS", "Credentials"
# def get_lists(sheet, worksheet):
#     wksheet = sheet.worksheet(worksheet)
#     # [1:] filter is needed to filted out headers row, as requested by Mr. Kroz
#     return wksheet.get_all_values()[1:]
#
#
# # sheet is an instance of google sheet - this is returned by add_gsheet somewhere in init section
# # worksheet is a sheet name, e.g. "RESERVATIONS", "Credentials"
# # values should be a list
# def add_row(sheet, worksheet, values):
#     wksheet = sheet.worksheet(worksheet)
#     wksheet.append_row(values)
#     return
#
# # sheet is an instance of google sheet - this is returned by add_gsheet somewhere in init section
# # worksheet is a sheet name, e.g. "RESERVATIONS", "Credentials"
# # id is a value of the ID - first column in a table
# # key is a horizontal offset/coordinate/column (starting from 1, not from zero sorry) - e.g. 1 = A, 2 = B in excel
# # value should be a integer/string which you want to write to the cell
# def update_row(sheet, worksheet, id, key, value):
#     wksheet = sheet.worksheet(worksheet)
#     #get a first column with ids
#     ids = wksheet.col_values(1)
#     #find which row our id is at
#     row = ids.index(id)
#     print(row)
#     wksheet.update_cell(row+1,key,value)
#     #update_cell(row, 4, id)
#     return


if __name__ == '__main__':
    test()
