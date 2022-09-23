# /usr/local/bin/python3
import datetime
import functools
import json
import subprocess
import sys
import threading


def date_flashback(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # flashback date
        date_setting = '20190101'
        today = datetime.date.today().strftime('%Y%m%d')
        GrpStart.run_cmd('echo "124124" | sudo date  -v +1d -f "%%Y%%m%%d" "%s" +%%F' % date_setting)
        res = func(*args, **kwargs)
        # redo date
        GrpStart.run_cmd('echo "124124" | sudo date  -v +1d -f "%%Y%%m%%d" "%s" +%%F' % today)
        return res

    return wrapper


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

    @date_flashback
    def start_or_stop(self, vm):
        try:
            res = GrpStart.run_cmd('prlctl %s %s' % (self.action, vm))
        except Exception as e:
            print(e)
        return res


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
