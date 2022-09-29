# /usr/local/bin/python3
import datetime
import json
import subprocess
import sys
import threading

SUDO_PASSWD = '124124'
SUDO = 'echo %s | sudo' % SUDO_PASSWD


class PreCheck(object):
    def __init__(self, func):
        self.func = func
        self.today = datetime.date.today().strftime('%Y%m%d')
        self.data_setting = '20190101'

    def __call__(self, *args, **kwargs):
        license_status = self.license_checker()['status']
        if license_status == 'ACTIVE':
            return self.func(*args, **kwargs)

        self.flaskback(self.data_setting)
        self.func(*args, **kwargs)
        self.flaskback(self.today)

        return

    def license_checker(self):
        res = json.loads(GrpStart.run_cmd('prlsrvctl info --license -j'))
        return res

    def flaskback(self, data):
        GrpStart.run_cmd('%s date  -v +1d -f "%%Y%%m%%d" "%s" +%%F' % (SUDO, data))


class PrlStart(threading.Thread):
    def __init__(self, func, args, name=''):
        super(PrlStart, self).__init__()
        self.name = name
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            return e


class GrpStart:
    valid_action = ('start', 'stop', 'pause', 'resume', 'suspend')

    def __init__(self, action, vm_group):
        assert action in self.valid_action, 'Action error. Valid actions: %s' % (' '.join(self.valid_action))
        self.vm_group = vm_group
        self.action = action

    @staticmethod
    def run_cmd(cmd):
        run_command = lambda x: ['/bin/sh', '-c', '%s' % x]
        res = subprocess.Popen(run_command(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        result = res.communicate()
        return '\n'.join(result)

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
            res = GrpStart.run_cmd('prlctl %s %s' % (self.action, vm))
            return res
        except Exception as e:
            print(e)


@PreCheck
def main():
    cmd = sys.argv[1:]
    action, vm_group = cmd
    start_vm = GrpStart(action, vm_group)
    vms = start_vm.filter_vm()
    try:
        thread_pool = []
        for vm in vms:
            p = PrlStart(start_vm.start_or_stop, (vm,))
            thread_pool.append(p)
        for i in thread_pool:
            i.start()
        for i in thread_pool:
            i.join()
            res = i.get_result()
            print(res)
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    main()
