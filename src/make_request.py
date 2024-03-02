import requests
import sys


def ping(url):
    stat, response = make_request('GET', 'http://' + url + '/ping')
    if stat:
        # print(f"Ответ от {url + '/ping'}: {response.text}")
        return True
    return False


def process_response(response):
    if response.status_code == 400:
        print(response.json()["error"])
        return False
    else:
        return True


def make_request(method, url, data=None, timeout=5):
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            print(data)
            response = requests.post(url, json=data)
        else:
            return "Неподдерживаемый метод запроса. Поддерживаемые методы: GET, POST."

        return process_response(response), response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP ошибка при выполнении запроса: {http_err}")
        return False, None
    except requests.exceptions.ConnectionError as conn_err:
        # print(f"Ошибка подключения при выполнении запроса: {conn_err}")
        return False, 503
    except requests.exceptions.Timeout as timeout_err:
        # print(f"Ошибка тайм-аута при выполнении запроса: {timeout_err}")
        return False, 503
    except requests.exceptions.RequestException as req_err:
        # print(f"Общая ошибка при выполнении запроса: {req_err}")
        return False, None
        # sys.exit()
