import threading
import os
import sys
import time
import queue
from netaddr import IPNetwork, core
from functools import wraps

ip_queue = queue.Queue()


def get_ips(cidr):
    # TODO: Need to fix when netmask not equal to 24
    try:
        ips = IPNetwork(cidr).iter_hosts()
        for ip in ips:
            ip_queue.put(ip)
    except core.AddrFormatError:
        print('Please enter the correct cidr or ip')
        sys.exit(1)


def ping(ip_queue):
    while not ip_queue.empty():
        ip = ip_queue.get()
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
    for i in range(1, 255):
        p = threading.Thread(target=ping, args=(ip_queue,))
        thread_pool.append(p)
    for i in thread_pool:
        i.start()
    for i in thread_pool:
        i.join()


if __name__ == '__main__':
    main()
