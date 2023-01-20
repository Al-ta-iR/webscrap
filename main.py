from dotenv import load_dotenv
import datetime as dt
import os
import platform
import re
import requests
import smtplib
import time


email_flag = 0
start_time = time.time()
is_os_windows = platform.system() == 'Windows'

if is_os_windows:
    env_path = os.path.join('secrets.env')  # ◄local ▼
    load_dotenv(env_path)
    EMAIL_SENDER = os.getenv('EMAIL_SENDER')
    PASSWORD_EMAIL_SENDER = os.getenv('PASSWORD_EMAIL_SENDER')
    EMAIL_RECIEVER = os.getenv('EMAIL_RECIEVER')
    SITE_DATA = os.getenv('SITE_DATA')
    PAGE_ID_SITE_DATA = os.getenv('PAGE_ID_SITE_DATA')
else:
    EMAIL_SENDER = os.environ.get('EMAIL_SENDER')  # online ▼
    PASSWORD_EMAIL_SENDER = os.environ.get('PASSWORD_EMAIL_SENDER')
    EMAIL_RECIEVER = os.environ.get('EMAIL_RECIEVER')
    SITE_DATA = os.environ.get('SITE_DATA')
    PAGE_ID_SITE_DATA = os.environ.get('PAGE_ID_SITE_DATA')



def finder_text(content, flag, board):
    left_id_position = content.find(flag) + len(flag)
    right_id_position = content[left_id_position : ].find(board) + left_id_position
    text = content[left_id_position : right_id_position]
    return text, right_id_position


def get_hub_data():
    json_data = {
        'page': {
            'id': PAGE_ID_SITE_DATA,
        },
        'limit': 100,
        'chunkNumber': 0,
        'verticalColumns': False,
    }

    # try:
    response = requests.post(SITE_DATA, json=json_data)
    # except Exception as e:
    #     print('Fail get data from Notion')
    # finally:
    #     pass

    all_data = str(response.text)
    value_flag = 'w[J":[["'
    find_id_position = all_data.find(value_flag) + len(value_flag)
    all_data = all_data[find_id_position + 1:]
    all_urls_data = []
    while 'https://' in all_data:
        value, end_position = finder_text(all_data, value_flag, '"')
        value = value.replace('\\\\', '\\')
        value = tuple(map(str, value.split('►')))
        value = tuple(filter(None, value))
        all_urls_data.append(value)

        url, end_position = finder_text(all_data, '"a","', '"')
        all_urls_data.append(url)

        all_data = all_data[end_position + 1:]
    return all_urls_data


def check_data(urls_data):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win32; x32; rv:106.0) Gecko/20100101 Firefox/106.0',
    }
    
    allert = ''
    change_counter = 0
    for i in range(0, len(urls_data), 2):
        if is_os_windows:
            print("Complete: ", round((100 / len(urls_data) * i), 1), "%", end="\r")
        response = requests.get(urls_data[i+1], headers=headers)
        status_code = response.status_code
        if status_code != 200:
            allert = allert + f'{status_code}: {urls_data[i+1]}\n------------\n'
            continue
        current_site_data = str(response.text)
        for value in urls_data[i]:
            if value[0] != '◄':
                if not bool(re.search(value, current_site_data)):
                    change_counter += 1
                    allert = allert + f'{change_counter}. [{urls_data[i+1]}] - not found [{value}]\n'
            else:
                if bool(re.search(value[1:], current_site_data)):
                    change_counter += 1
                    allert = allert + f'{change_counter}. [{urls_data[i+1]}] - found [{value[1:]}]\n'

    if allert != '':
        message_router(allert, change_counter)


def send_mail(
    subject,
    text
):
    try:
        message = 'Subject: {}\n\n{}'.format(subject, f'{text}')
        server = smtplib.SMTP_SSL('mail.inbox.lv', 465)
        server.login(EMAIL_SENDER, PASSWORD_EMAIL_SENDER)
        server.sendmail(EMAIL_SENDER, EMAIL_RECIEVER, message)
        server.quit()
    except Exception as e:
        print(f'Email did not send: {e}')
    finally:
        pass

def message_router(allert, change_counter):
    time_work = "\n--- %s seconds ---\n" % round((time.time() - start_time), 2)
    message = allert + time_work
    if is_os_windows:
        print(f'Изменений: {change_counter}{10*" "}', '\n', message)
    else:
        send_mail(f'Changes on monitored sites: {change_counter}', allert)

if __name__ == '__main__':
    urls_data = get_hub_data()
    check_data(urls_data)
