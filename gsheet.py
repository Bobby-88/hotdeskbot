import gspread


def add_gsheet():
    gc = gspread.service_account(filename='gsheet-credentials.json')
    sh = gc.open("Help")
    # offices_worksheet = sh.worksheet("Offices")
    # offices = offices_worksheet.col_values(1)
    print(sh.sheet1.get('A1'))
    # print(offices)
    return sh


def get_offices(sh):
    offices_worksheet = sh.worksheet("Offices")
    offices = offices_worksheet.col_values(1)
    return offices


def get_users(sh):
    credentials_worksheet = sh.worksheet("Credentials")
    users = credentials_worksheet.get_all_values()
    # print(users)
    return users


def persist_user_id(sh, row, id):
    credentials_worksheet = sh.worksheet("Credentials")
    credentials_worksheet.update_cell(row, 4, id)
    # users = credentials_worksheet.get_all_values()
    # print(users)
    return


# this gets a list of lists from a gsheet.
# sheet is an instance of google sheet - this is returned by add_gsheet somewhere in init section
# worksheet is a sheet name, e.g. "RESERVATIONS", "Credentials"
def get_lists(sheet, worksheet):
    wksheet = sheet.worksheet(worksheet)
    # [1:] filter is needed to filted out headers row, as requested by Mr. Kroz
    return wksheet.get_all_values()[1:]


# todo add description
# values should be a list
def add_row(sheet, worksheet, values):
    wksheet = sheet.worksheet(worksheet)
    wksheet.append_row(values)
    return
