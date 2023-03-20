from dotenv import load_dotenv
from urllib.parse import unquote
# import datetime as dt
import os
import platform
import re
import requests
import smtplib
import concurrent.futures
import time
import urllib.parse
from search_data import get_hub_data


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
    RUTRACKER_LOGIN_USERNAME = os.getenv('RUTRACKER_LOGIN_USERNAME')
    RUTRACKER_LOGIN_PASSWORD = os.getenv('RUTRACKER_LOGIN_PASSWORD')
else:
    EMAIL_SENDER = os.environ.get('EMAIL_SENDER')  # online ▼
    PASSWORD_EMAIL_SENDER = os.environ.get('PASSWORD_EMAIL_SENDER')
    EMAIL_RECIEVER = os.environ.get('EMAIL_RECIEVER')
    SITE_DATA = os.environ.get('SITE_DATA')
    PAGE_ID_SITE_DATA = os.environ.get('PAGE_ID_SITE_DATA')
    RUTRACKER_LOGIN_USERNAME = os.environ.get('RUTRACKER_LOGIN_USERNAME')
    RUTRACKER_LOGIN_PASSWORD = os.environ.get('RUTRACKER_LOGIN_PASSWORD')


def search_string(search_trigger, url, value, change_counter, current_site_data, is_equals):
    allert = ""
    start = value.find(search_trigger)
    end = value.find(':')
    flag_counter_string = value[start+len(search_trigger):end]
    if not flag_counter_string.isnumeric():
        allert += f'Flag {value} does not have number'
        return allert
    flag_counter = int(flag_counter_string)
    flag_search = value.split(":", 1)[1]
    count = current_site_data.count(flag_search)
    if (count == flag_counter) is is_equals:
        return ''
    else:
        change_counter += 1
        allert += f'{change_counter}. [{url.encode()}]\n  - flag [{flag_search.encode()}] {("needed" if is_equals else "NOT needed")} {flag_counter} - found {count}\n'
        return allert


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win32; x32; rv:106.0) Gecko/20100101 Firefox/111.0',
}

def check_url(url_data):
    url, flag = url_data
    allert = ''
    change_counter = 0
    if '▼' in flag[0]:
        return allert, change_counter
    
    try:
        redirect = True
        if '▲' in flag[0]:
            redirect = False
        if 'rutracker' in url:
            data = {
                "redirect": url[28:].replace("/", ""),
                "login_username": RUTRACKER_LOGIN_USERNAME,
                "login_password": RUTRACKER_LOGIN_PASSWORD,
                "login": "%C2%F5%EE%E4",
            }
            response = requests.post("https://rutracker.org/forum/login.php", headers=headers, allow_redirects=redirect, data=data)
        else:
            response = requests.get(url, headers=headers, allow_redirects=redirect)
    except Exception as e:
        allert += f'URL: {url} has problem: {e}\n'
        return allert, change_counter
    
    status_code = response.status_code
    if status_code != 200:
        if '◄' not in flag[0]:
            allert += f'{status_code}: {url}\n'
        return allert, change_counter
    
    current_site_data = str(response.text)
    for value in flag:
        search_trigger = '∟∟'
        if value[0] != '◄':
            if search_trigger in value:
                allert += search_string(search_trigger, url, value, change_counter, current_site_data, True)
                continue
            if not bool(re.search(value, current_site_data)):
                change_counter += 1
                allert += f'{change_counter}. [{url.encode()}]\n  - not found [{value.encode()}]\n'
        else:
            if search_trigger in value:
                allert += search_string(search_trigger, url, value, change_counter, current_site_data, False)
                continue
            if re.search(value[1:], current_site_data):
                change_counter += 1
                allert += f'{change_counter}. [{url.encode()}]\n  - found [{value[1:].encode()}]\n'
    
    return allert, change_counter


def check_data(urls_data):
    allert = ''
    allert_status = ''
    change_counter = 0
    url_data = [(urllib.parse.unquote(urls_data[i+1]), urls_data[i]) for i in range(0, len(urls_data), 2)]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(check_url, url_data)
    
    for result in results:
        allert += result[0]
        change_counter += result[1]
    
    if allert != '':
        message = 'Changes:\n' + allert
        message_router(message, change_counter)


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
        if is_os_windows:
            print(f'Email did not send: {e}')
        server.sendmail(EMAIL_SENDER, EMAIL_RECIEVER, 'Subject: {}\n\n{}'.format('error', 'error'))
    finally:
        pass

def message_router(allert, change_counter):
    time_work = "\n--- %s seconds ---\n" % round((time.time() - start_time), 2)
    message = (allert + time_work)
    if is_os_windows:
        print()
        print(f'Изменений: {change_counter}{10*" "}\n{message}')
        # send_mail(f'Changes on monitored sites: {change_counter}', message)
    else:
        send_mail(f'Changes on monitored sites: {change_counter}', message)

if __name__ == '__main__':
    urls_data = get_hub_data(PAGE_ID_SITE_DATA, SITE_DATA)
    check_data(urls_data)
