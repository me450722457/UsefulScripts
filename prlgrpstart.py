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
    run_command = lambda x: ['/bin/sh', '-c', '%s' % x]

    def __init__(self, grpname):
        self.grpname = grpname

    @staticmethod
    def run_cmd(cmd):
        res = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        result = res.communicate()[0]
        return result

    @staticmethod
    def get_vm_info():
        cmd = GrpStart.run_command('prlctl list -ij')
        res = GrpStart.run_cmd(cmd)
        return res

    def filter_vm(self):
        vm_info = self.get_vm_info()
        vm_info = json.loads(vm_info)
        vm_to_start = []
        for vm in vm_info:
            if vm.get('Description') == self.grpname:
                vm_to_start.append(vm.get('Name'))
        return vm_to_start

    def start_vm(self, vm):
        vm_start_cmd = GrpStart.run_command('prlctl start %s' % vm)
        try:
            self.run_cmd(vm_start_cmd)
        except Exception as e:
            print(e)


def main():
    grpname = sys.argv[1]
    startvm = GrpStart(grpname)
    vms = startvm.filter_vm()
    thread_pool = []
    for vm in vms:
        p = PrlStart(startvm.start_vm, (vm,))
        thread_pool.append(p)
    for i in thread_pool:
        i.start()
    for i in thread_pool:
        i.join()


if __name__ == '__main__':
    main()
