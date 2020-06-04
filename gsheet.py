import gspread


def add_gsheet():
    gc = gspread.service_account(filename='gsheet-credentials.json')
    sh = gc.open("hotdesk")
    print(sh.sheet1.get('A1'))
