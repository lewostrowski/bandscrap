import argparse
from colorama import Fore, Style
from scenario import Scenario
import requests


def console_decorator(func):
    def wrapper(*args, **kwargs):
        code, results = func(*args, **kwargs)

        if code == 200:
            print('Status: ' + Fore.GREEN + str(code) + Style.RESET_ALL)
            if results:
                print('--------------------')
                print(results)
                print('--------------------')

        elif code == 204:
            print('Status: ' + Fore.YELLOW + str(code) + Style.RESET_ALL)
            if results:
                print('--------------------')
                print(results)
                print('--------------------')

        else:
            print('Status: ' + Fore.RED + str(code) + Style.RESET_ALL)
            print('--------------------')
            print(results)
            print('--------------------')
    return wrapper


class TestApi:
    def __init__(self, serv):
        self.serv = serv if not serv.endswith('/') else serv[:-1]

    @console_decorator
    def get(self, link):
        address = '{}/{}'.format(self.serv, link)

        print(Style.BRIGHT + 'Testing GET on: {}'.format(address) + Style.RESET_ALL)

        try:
            response = requests.get(address)
            if response.status_code == 200:
                return response.status_code, response.text
            else:
                return response.status_code, ''
        except requests.exceptions.ConnectionError as e:
            return 0, e

    @console_decorator
    def post(self, link, data):
        address = '{}/{}'.format(self.serv, link)
        headers = {'Content-type': 'application/json'}

        print(Style.BRIGHT + 'Testing POST on: {}'.format(address) + Style.RESET_ALL)

        try:
            response = requests.post(address, data=data, headers=headers)
            if response.status_code == 200:
                return response.status_code, response.text
            else:
                return response.status_code, ''
        except requests.exceptions.ConnectionError as e:
            return 0, e

    @console_decorator
    def delete(self, link):
        address = '{}/{}'.format(self.serv, link)

        print(Style.BRIGHT + 'Testing DELETE on: {}'.format(address) + Style.RESET_ALL)

        try:
            response = requests.delete(address)
            if response.status_code == 200:
                return response.status_code, response.text
            else:
                return response.status_code, ''
        except requests.exceptions.ConnectionError as e:
            return 0, e

    @console_decorator
    def put(self, link):
        address = '{}/{}'.format(self.serv, link)

        print(Style.BRIGHT + 'Testing PUT on: {}'.format(address) + Style.RESET_ALL)

        try:
            response = requests.put(address)
            if response.status_code == 200:
                return response.status_code, response.text
            else:
                return response.status_code, ''
        except requests.exceptions.ConnectionError as e:
            return 0, e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Api testing unit.')
    parser.add_argument('-g', help='Send GET request to specific endpoint.')
    parser.add_argument('-p', help='Send POST request to specific endpoint.')
    parser.add_argument('-d', help='Send DELETE request to specific endpoint.')
    parser.add_argument('-u', help='Send PUT request to specific endpoint.')
    parser.add_argument('-b', help='Json body to send.')
    args = parser.parse_args()

    unit = TestApi('http://127.0.0.1:5000')

    # python test.py [flag] [endpoint] [flag] [json body]
    # python test.py -p search -b '{"key": "val"}'

    if args.g:
        unit.get(link=args.g)
    elif args.d:
        unit.delete(link=args.d)
    elif args.u:
        unit.put(link=args.u)
    elif args.p and args.b:
        unit.post(link=args.p, data=args.b)




