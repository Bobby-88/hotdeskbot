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
    #print(users)
    return users

def persist_user_id(sh, row, id):
    credentials_worksheet = sh.worksheet("Credentials")
    credentials_worksheet.update_cell(row, 4, id)
    #users = credentials_worksheet.get_all_values()
    #print(users)
    return