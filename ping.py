import threading
import os
import sys
import time
from netaddr import IPNetwork, core
from functools import wraps

ip_list = []


class MyPing(threading.Thread):
    def __init__(self, func, args, name=''):
        super(MyPing, self).__init__()
        self.name = name
        self.func = func
        self.args = args

    def run(self):
        self.func(*self.args)


def get_ips(cidr):
    try:
        ips = IPNetwork(cidr).iter_hosts()
        for ip in ips:
            ip_list.append(ip.format())
    except core.AddrFormatError:
        print('Please enter the correct cidr or ip')
        sys.exit(1)


def ping(ip):
    res = os.system('ping -c 1 %s 2>&1 >> /dev/null' % (ip))
    if not res:
        print('Success on %s' % ip)


def exec_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        print("Total time:", end_time - start_time)
    return wrapper


@exec_time
def main():
    # TODO: Add usage
    cidr = str(sys.argv[1])
    get_ips(cidr)
    thread_pool = []
    for ip in ip_list:
        p = MyPing(ping, (ip,))
        thread_pool.append(p)
    for i in thread_pool:
        i.start()
    for i in thread_pool:
        i.join()


if __name__ == '__main__':
    main()
