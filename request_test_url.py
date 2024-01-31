import json
import os
import re
import requests
import uncurl



def make_request_from_curl_obj(context):
    # Распаковать объект запроса
    method = context.method
    url = context.url
    data = context.data
    headers = context.headers
    cookies = context.cookies
    auth = context.auth
    proxies = None
    if 'proxies' in context:
        proxies = context.proxies

    # Сделать запрос
    if method.upper() == 'GET':
        response = requests.get(url, headers=headers, cookies=cookies, auth=auth, proxies=proxies)
    elif method.upper() == 'POST':
        response = requests.post(url, data=data, headers=headers, cookies=cookies, auth=auth, proxies=proxies)
    else:
        raise ValueError(f'Метод {method} не поддерживается')
    return response


def response_to_txt(url, response):
    url_parts = re.split(r'[.-]', url, maxsplit=1)
    first_url_part = url_parts[0][8:]
    with open(os.path.join(os.environ['USERPROFILE'], 'Desktop', f'{first_url_part}.txt'), 'w') as f:
        f.write(f'URL: {url}\n---\n')
        f.write(f'Response: {response.text}\n=========')
        print(first_url_part)


def main():
    method = input("Введите метод (get, post, put, delete): ")
    url = input("Введите ссылку на сайт: ")

    if "curl" in url:
        context = uncurl.parse_context(url)
        response = make_request_from_curl_obj(context)
        # response = os.system(url)
        curl_parts = re.split('https://', url, maxsplit=1)
        url_part_from_curl = curl_parts[1][:30]
        response_to_txt(f'https://{url_part_from_curl}', response)

    else:
        if method == "get":
            response = requests.get(url)
        elif method in ["put", "post", "delete"]:
            data_type = input("Введи тип передаваемой информации (data или json): ")
            data = json.loads(input("Введи " + data_type + ' в {} 1-й строкой, ключи в "": '))
            headers_text = json.loads(input('Введи headers в {} 1-й строкой, ключи в "", начиная с "host": '))

            if data_type == "data":
                response = requests.request(method, url, data=data, headers=headers_text)
            elif data_type == "json":
                response = requests.request(method, url, json=data, headers=headers_text)

        print(response.status_code)

        if response.status_code not in (200, 201):
            return False
        response_to_txt(url, response)


if __name__ == "__main__":
    main()
