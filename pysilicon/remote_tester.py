import paramiko
import time

class RemoteTester:

    def __init__(password):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect("mp_ubuntu.andrew.cmu.edu", username="mpubuntu", password=password, port="22")
        time.sleep(5)

    def exec_ssh(self, cmd, ret = False):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        if not ret:
            [print(i[:-1]) for i in stdout.readlines()]
            [print(i[:-1]) for i in stderr.readlines()]
        return stdout.readlines()

    def exec_visa(self, params, ret = False):
        return exec_ssh(f"python3 /home/mpubuntu/projects/i22j_test/equipment_control.py {params}", ret = ret)
