# -*- coding: utf-8 -*-

"""
@Author: Tireless
@software: PyCharm
@time: 2022/10/15 9:42
"""

import threading
import time
import requests
import urllib.request

if bytes is str: input = raw_input

try:

    def get_func(url, *args, **kwargs):
        resp = requests.get(url, *args, **kwargs)
        return resp.text


    def post_func(url, data, *args, **kwargs):
        resp = requests.post(url, data=data, *args, **kwargs)
        return resp.text

except ImportError:

    def get_func(url, *args, **kwargs):
        req = urllib.request.Request(url, *args, **kwargs)
        resp = urllib.request.urlopen(req)
        return resp.read().decode("utf-8")


    def post_func(url, data, *args, **kwargs):
        data_bytes = bytes(urllib.parse.urlencode(data), encoding='utf-8')
        req = urllib.request.Request(url, data=data_bytes, *args, **kwargs)
        resp = urllib.request.urlopen(req)
        return resp.read().decode("utf-8")


def time2date(timestamp):
    time_arry = time.localtime(int(timestamp))
    return time.strftime('%Y-%m-%d %H:%M:%S', time_arry)


def humanable_bytes(num_byte):
    num_byte = float(num_byte)
    num_GB, num_MB, num_KB = 0, 0, 0
    if num_byte >= 1024 ** 3:
        num_GB = num_byte // (1024 ** 3)
        num_byte -= num_GB * (1024 ** 3)
    if num_byte >= 1024 ** 2:
        num_MB = num_byte // (1024 ** 2)
        num_byte -= num_MB * (1024 ** 2)
    if num_byte >= 1024:
        num_KB = num_byte // 1024
        num_byte -= num_KB * 1024
    return '{} GB {} MB {} KB {} B'.format(num_GB, num_MB, num_KB, num_byte)


def humanable_bytes2(num_byte):
    num_byte = float(num_byte)
    if num_byte >= 1024 ** 3:
        return '{:.2f} GB'.format(num_byte / (1024 ** 3))
    elif num_byte >= 1024 ** 2:
        return '{:.2f} MB'.format(num_byte / (1024 ** 2))
    elif num_byte >= 1024 ** 1:
        return '{:.2f} KB'.format(num_byte / (1024 ** 1))


class SrunClient:
    name = 'CUGB'
    srun_ip = '' # 自己学校认证ip，格式为#.#.#.# 例如123.123.123.123

    login_url = 'http://{}/cgi-bin/srun_portal'.format(srun_ip)
    online_url = 'http://{}/cgi-bin/rad_user_info'.format(srun_ip)
    # headers = {'User-Agent': 'SrunClient {}'.format(name)}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}

    def __init__(self, username=None, passwd=None, print_log=True):
        self.username = username
        self.passwd = passwd
        self.print_log = print_log
        self.check_status = 0
        self.online_info = dict()
        self.check_online()

    def _encrypt(self, passwd):
        column_key = [0, 0, 'd', 'c', 'j', 'i', 'h', 'g']
        row_key = [
            ['6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E'],
            ['?', '>', 'A', '@', 'C', 'B', 'E', 'D', '7', '6', '9', '8', ';', ':', '=', '<'],
            ['>', '?', '@', 'A', 'B', 'C', 'D', 'E', '6', '7', '8', '9', ':', ';', '<', '='],
            ['=', '<', ';', ':', '9', '8', '7', '6', 'E', 'D', 'C', 'B', 'A', '@', '?', '>'],
            ['<', '=', ':', ';', '8', '9', '6', '7', 'D', 'E', 'B', 'C', '@', 'A', '>', '?'],
            [';', ':', '=', '<', '7', '6', '9', '8', 'C', 'B', 'E', 'D', '?', '>', 'A', '@'],
            [':', ';', '<', '=', '6', '7', '8', '9', 'B', 'C', 'D', 'E', '>', '?', '@', 'A'],
            ['9', '8', '7', '6', '=', '<', ';', ':', 'A', '@', '?', '>', 'E', 'D', 'B', 'C'],
            ['8', '9', '6', '7', '<', '=', ':', ';', '@', 'A', '>', '?', 'D', 'E', 'B', 'C'],
            ['7', '6', '8', '9', ';', ':', '=', '<', '?', '>', 'A', '@', 'C', 'B', 'D', 'E'],
        ]
        encrypt_passwd = ''
        for idx, c in enumerate(passwd):
            char_c = column_key[ord(c) >> 4]
            char_r = row_key[idx % 10][ord(c) & 0xf]
            if idx % 2:
                encrypt_passwd += char_c + char_r
            else:
                encrypt_passwd += char_r + char_c
        return encrypt_passwd

    def _log(self, msg):
        if self.print_log:
            print('[SrunClient {}] {}'.format(self.name, msg))

    def check_online(self):
        resp_text = get_func(self.online_url, headers=self.headers)
        if 'not_online' in resp_text:
            self._log('###*** NOT ONLINE! ***###')
            return False
        try:
            items = resp_text.split(',')
            self.online_info = {
                'online': True, 'username': items[0],
                'login_time': items[1], 'now_time': items[2],
                'used_bytes': items[6], 'used_second': items[7],
                'ip': items[8], 'balance': items[11],
                'auth_server_version': items[21]
            }
            return True
        except Exception as e:
            print(resp_text)
            print('Catch `Status Internal Server Error`? The request is frequent!')
            print(e)

    def show_online(self):
        if not self.check_online(): return
        self._log('###*** ONLINE INFORMATION! ***###')
        header = '================== ONLIN INFORMATION =================='

        print(header)
        print('Username: {}'.format(self.online_info['username']))
        print('Login time: {}'.format(time2date(self.online_info['login_time'])))
        print('Now time: {}'.format(time2date(self.online_info['now_time'])))
        print('Used data: {}'.format(humanable_bytes(self.online_info['used_bytes'])))
        print('Ip: {}'.format(self.online_info['ip']))
        print('Balance: {}'.format(self.online_info['balance']))
        print('=' * len(header))

    def login(self):
        if self.check_online():
            self._log('###*** ALREADY ONLINE! ***###')
            return True
        if not self.username or not self.passwd:
            self._log('###*** LOGIN FAILED! (username or passwd is None) ***###')
            self._log('username and passwd are required! (check username and passwd)')
            return False
        encrypt_passwd = self._encrypt(self.passwd)
        payload = {
            'action': 'login',
            'username': self.username,
            'password': encrypt_passwd,
            'type': 2, 'n': 117,
            'drop': 0, 'pop': 0,
            'mbytes': 0, 'minutes': 0,
            'ac_id': 1
        }
        resp_text = post_func(self.login_url, data=payload, headers=self.headers)
        if 'login_ok' in resp_text:
            self._log('###*** LOGIN SUCCESS! ***###')
            self._log(resp_text)
            self.show_online()
            return True
        elif 'login_error' in resp_text:
            self._log('###*** LOGIN FAILED! (login error)***###')
            self._log(resp_text)
            return False
        else:
            self._log('###*** LOGIN FAILED! (unknown error) ***###')
            self._log(resp_text)
            return False

    def logout(self):
        if not self.check_online(): return True
        payload = {
            'action': 'logout',
            'ac_id': 1,
            'username': self.online_info['username'],
            'type': 2
        }
        resp_text = post_func(self.login_url, data=payload, headers=self.headers)
        if 'logout_ok' in resp_text:
            self._log('###*** LOGOUT SUCCESS! ***###')
            return True
        elif 'login_error' in resp_text:
            self._log('###*** LOGOUT FAILED! (login error) ***###')
            self._log(resp_text)
            return False
        else:
            self._log('###*** LOGOUT FAILED! (unknown error) ***###')
            self._log(resp_text)
            return False

    def thread_check_online(self):
        resp_text = get_func(self.online_url, headers=self.headers)
        if 'not_online' in resp_text:
            self._log('###*** NOT ONLINE! ***###')
            self._log("NOT ONLINE, TRY TO LOGIN!")
            self.login()
            self.check_status += 1
        print('\r', '当前已自动重连{:d}次'.format(self.check_status), end='')


def show_commands():
    wellcome = '############### Wellcome to Srun Client ###############'
    print(wellcome)
    print('[1]: show online information')
    print('[2]: set username and passwd')
    print('[3]: login')
    print('[4]: logout')
    print('[5]: thread check network')
    print('[h]: show this messages')
    print('[q]: quit')
    print('#' * len(wellcome))


class myThread(threading.Thread):
    def __init__(self, threadID, name, srun_client):
        threading.Thread.__init__(self)
        self.srun_client = srun_client
        self.threadID = threadID
        self.name = name

    def run(self):
        print("开始线程：" + self.name)
        while True:
            self.srun_client.thread_check_online()
            time.sleep(1)


if __name__ == "__main__":
    srun_client = SrunClient()
    srun_client.username = "" # 修改自己深澜账号
    srun_client.passwd = "" #深澜密码
    show_commands()
    srun_client.show_online()
    command = '_'
    while command != 'q':
        command = input('>')
        if command == '1':
            srun_client.show_online()
        elif command == '2':
            srun_client.username = input('username: ')
            # srun_client.passwd = getpass.getpass('passwd: ')
            srun_client.passwd = input('passwd: ')
        elif command == '3':
            srun_client.login()
        elif command == '4':
            srun_client.logout()
        elif command == '5':
            thread = myThread(1, "start thread", srun_client)
            # 开启线程
            thread.start()
        elif command == 'h':
            show_commands()
        elif command == 'q':
            print('bye!')
        else:
            print('unknown command!')
