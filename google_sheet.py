import httplib2
import json
import os

from apiclient import discovery
from google.oauth2 import service_account


def google_sheet_get_data(GOOGLE_CREDENTIALS_VAL):
    try:
        scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/spreadsheets",
        ]
        secret = json.loads(GOOGLE_CREDENTIALS_VAL)

        spreadsheet_id = "1G2nXkcyPnGvFHOZnZAG_BJVdiYwjyNxdbUT51U5Acuw"
        # range_name = 'WebScrap!A1:L50'

        credentials = service_account.Credentials.from_service_account_info(
            secret, scopes=scopes
        )
        service = discovery.build("sheets", "v4", credentials=credentials)

        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range="WebScrap")
            .execute()
        )
        rows = result.get("values", [])

        is_parse = False
        urls_data = []
        for row in rows:
            if not is_parse and "№" not in row and "Result" not in row:
                continue
            if not is_parse and "№" in row and "Result" in row:
                is_parse = True
                continue
            if "===END===" in row:
                is_parse = False
                break
            elif is_parse:
                is_needed_item = False
                for item in row:
                    if item != "" and ("http" in item or "www." in item):
                        urls_data.append(item)
                        is_needed_item = True
                    elif is_needed_item:
                        item = item.split("►")
                        # for keys in item:
                        urls_data.append(item)

                        is_needed_item = False
        #         value = tuple(map(str, value.split('►')))
        return urls_data

    except OSError as e:
        print(e)
        return False


# import pygsheets


# def google_sheet_get_data(sheet_name, CLIENT_SECRETS_GOOGLE):
#     if CLIENT_SECRETS_GOOGLE == '':
#         gc = pygsheets.authorize()
#     else:
#         gc = pygsheets.authorize(CLIENT_SECRETS_GOOGLE)

#     # Open spreadsheet and then worksheet
#     sh = gc.open(sheet_name)
#     wks = sh.sheet1
#     values = wks.get_all_values()
#     is_parse = False
#     urls_data = []
#     for row in values:
#         if not is_parse and "№" not in row and "Result" not in row:
#             continue
#         if not is_parse and "№" in row and "Result" in row:
#             is_parse = True
#             continue
#         if "===END===" in row:
#             is_parse = False
#             break
#         elif is_parse:
#             is_needed_item = False
#             for item in row:
#                 if item != '' and ('http' in item or 'www.' in item):
#                     urls_data.append(item)
#                     is_needed_item = True
#                 elif is_needed_item:
#                     item = item.split('►')
#                     # for keys in item:
#                     urls_data.append(item)

#                     is_needed_item = False
# #         value = tuple(map(str, value.split('►')))

#     return urls_data


# if __name__ == '__main__':
#     urls_data = google_sheet_get_data('Os.. ... ..nt', '')
#     print(urls_data)
