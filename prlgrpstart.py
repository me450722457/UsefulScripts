# /usr/local/bin/python3

import subprocess
import json
import threading
import sys


class PrlStart(threading.Thread):
    def __init__(self, func, args, name=''):
        super(PrlStart, self).__init__()
        self.name = name
        self.func = func
        self.args = args

    def run(self):
        self.func(*self.args)


class GrpStart:
    def __init__(self, action, vm_group):
        assert action in ('start', 'stop'), 'Action error. Only start or stop'
        self.vm_group = vm_group
        self.action = action

    @staticmethod
    def run_cmd(cmd):
        run_command = lambda x: ['/bin/sh', '-c', '%s' % x]
        res = subprocess.Popen(run_command(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        result = res.communicate()[0]
        return result

    @staticmethod
    def get_vm_info():
        res = GrpStart.run_cmd('prlctl list -ij')
        return res

    def filter_vm(self):
        vm_info = self.get_vm_info()
        vm_info = json.loads(vm_info)
        for vm in vm_info:
            if vm.get('Description') == self.vm_group:
                yield vm.get('Name')

    def start_or_stop(self, vm):
        try:
            GrpStart.run_cmd('prlctl %s %s' % (self.action, vm))
        except Exception as e:
            print(e)


def main():
    cmd = sys.argv[1:]
    action, vm_group = cmd
    start_vm = GrpStart(action, vm_group)
    vms = start_vm.filter_vm()
    thread_pool = []
    for vm in vms:
        p = PrlStart(start_vm.start_or_stop, (vm,))
        thread_pool.append(p)
    for i in thread_pool:
        i.start()
    for i in thread_pool:
        i.join()


if __name__ == '__main__':
    main()
