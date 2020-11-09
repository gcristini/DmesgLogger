import subprocess
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell import exceptions
from Libraries.Timer import Timer
import sys
import json

class ADB_Error(Exception):
    # TODO
    pass

class SX5_Manager(object):
    """ """
    # ************************************************* #
    # **************** Private Methods **************** #
    # ************************************************* #
    def __init__(self):
        """ Constructor"""
        
        self._sx5_config_dict: dict
        self._sx5_device: AdbDeviceTcp

        pass

    # ---------------------------------------------------------------- #
    # ----------------------- Private Methods ------------------------ #
    # ---------------------------------------------------------------- #
    def _parse_config_file(self):
        """"""
        with open("Config.json") as json_file:
            self._sx5_config_dict = json.load(json_file)

        pass

    def _adb_init(self):
        """"""
        count = 0
        res = -1
        num_of_try = 60

        # Start Timer
        timer = Timer()
        timer.start()

        while (count < num_of_try):
            if timer.elapsed_time_s(2) >= 1:
                print("- Waiting for SX5 device " + "."*count, end='\r')
                res = subprocess.run("adb devices", text=True, capture_output=True).stdout.find(self._sx5_config_dict['device']['name'])
                if (res != -1):
                    timer.stop()
                    break
                else:
                    timer.reset()

                count += 1
        if res == -1:
            sys.stdout.write("\033[K")
            print("No Device Found")
            raise ADB_Error
        else:
            sys.stdout.write("\033[K")
            self._sx5_device = AdbDeviceTcp(host=self._sx5_config_dict['device']['ip'],
                                            port=int(self._sx5_config_dict['device']['port']),
                                            default_transport_timeout_s=9.)
        pass

    def _adb_tcp_connect(self):
        """"""
        try:
            self._sx5_device.connect(auth_timeout_s=0.1)
            print("- SX5 Connected")
        except:
            print("Timeout expired: check if device is on and if the IP is correct")
            raise
        pass

    def _adb_tcp_disconnect(self):
        """"""
        self._sx5_device.close()
        pass

    # ---------------------------------------------------------------- #
    # ------------------------ Public Methods ------------------------ #
    # ---------------------------------------------------------------- #

    def init(self):
        """ Initialize class and connect SX5 to ADB over TCP-IP protocol """
        # Parse config file
        self._parse_config_file()

        # Initialize adb connection
        try:
            self._adb_init()
        except ADB_Error:
            sys.exit()
        try:
            self._adb_tcp_connect()
        except:
            subprocess.run("adb disconnect")
            subprocess.run("adb tcpip {port}".format(port=int(self._sx5_config_dict['device']['port'])))
            #self._adb_init()
            self._adb_tcp_connect()
        pass

    def _read_shell(self, cmd: str):
        """"""
        max_attempt = 10
        attempt_count = 0
        stdout = ""

        while attempt_count < max_attempt:
            try:
                #stdout = self._sx5_device.shell(cmd)
                stdout=subprocess.run(f'adb shell "{cmd}"', text=True, capture_output=True).stdout
            except:
                # Try to establish a new connection if no response...
                try:
                    self._sx5_device = AdbDeviceTcp(host=self._sx5_config_dict['device']['ip'],
                                                    port=int(self._sx5_config_dict['device']['port']),
                                                    default_transport_timeout_s=9.)
                except:
                    pass
                try:
                    self._sx5_device.connect(auth_timeout_s=0.2)
                except:
                    pass

                attempt_count += 1
            else:
                break

        if attempt_count >= max_attempt:
            raise exceptions.TcpTimeoutException
        pass

        return stdout

    def read_dmesg(self):
        """ """
        # TODO fare check
        #stdout = self._read_shell('adb shell "dmesg -c -T"')
        stdout = self._read_shell('dmesg -c')

        return stdout
        







