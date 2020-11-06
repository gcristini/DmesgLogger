#!/usr/bin/env python

import sys
import os
import subprocess
import time
import json

import colorama as cm


#from Libraries.Enums import Enums as en
#from Libraries.ParseXml import XmlDictConfig
#from xml.etree import ElementTree

from Libraries.Timer import Timer
from Libraries.SX5_Manager import SX5_Manager
from adb_shell import exceptions

class MainStateEnum:
    MAIN_STATE_INIT = "init"
    MAIN_STATE_CREATE_FOLDER = "create_folder"
    MAIN_STATE_ADB_CONNECT = "adb_connect"
    MAIN_STATE_DMESG = "dmesg"
    MAIN_STATE_STOP = "stop"
    MAIN_STATE_EXIT = "exit"


class Main(object):
    """ """

    # ************************************************* #
    # **************** Private Methods **************** #
    # ************************************************* #
    def __init__(self):
        """ Constructor """
        
        self._main_config_dict: dict
        self._log_file_dict = {
            "storage": "",
            "log_files": {}
        }

        self._sx5: SX5_Manager

        self._global_timer: Timer

        # State Machine
        self._main_state_fun_dict = {
            MainStateEnum.MAIN_STATE_INIT: self._init_state_manager,
            MainStateEnum.MAIN_STATE_CREATE_FOLDER: self._create_folder_state_manager,
            MainStateEnum.MAIN_STATE_ADB_CONNECT: self._adb_connect_state_manager,
            MainStateEnum.MAIN_STATE_DMESG: self._dmesg_state_manager,
            MainStateEnum.MAIN_STATE_STOP: self._stop_state_manager,
            MainStateEnum.MAIN_STATE_EXIT: self._exit_state_manager
        }

        self._main_state: None
        self._last_main: None



    # ---------------------------------------------------------------- #
    # ----------------------- Private Methods ------------------------ #
    # ---------------------------------------------------------------- #
    @staticmethod
    def _print_help():
        """"""
        pass

    def _parse_config_file(self):
        """"""
        # Read .json configuration file and store data into dictionary
        with open("Config.json") as json_file:
            self._main_config_dict = json.load(json_file)

        print (self._main_config_dict)
                
        return

    # ------------------ STATE MACHINE ------------------ #
    def _go_to_next_state(self, state):
        """"""
        # Store last state
        self._store_last_state()

        # Go to next state
        self._main_state = state
        return

    def _store_last_state(self):
        self._last_main_state = self._main_state
        return

    def _init_state_manager(self):
        """"""
        print(cm.Fore.MAGENTA + " ------------------------------------------------------------ ")
        print(cm.Fore.MAGENTA + " ----------------- WELCOME TO DMESG LOGGER! ----------------- ")
        print(cm.Fore.MAGENTA + " ------------------------------------------------------------ ")
        
        self._sx5.init()

        self._global_timer.start()

        # Go to create folder state
        self._go_to_next_state(MainStateEnum.MAIN_STATE_CREATE_FOLDER)
        return
    
    def _create_folder_state_manager(self):
        """"""
        # Create storage directory adding _n if already exists
        self._log_file_dict["storage"] = f'{os.getcwd()}/{self._main_config_dict["device"]["name"]}'       
        if os.path.isdir(self._log_file_dict["storage"]):
            for n in range (1, 999):            
                new_storage_folder = f'{self._log_file_dict["storage"]}_{n}'
                if not os.path.isdir(new_storage_folder):
                    self._log_file_dict["storage"] = new_storage_folder
                    break

        os.mkdir(self._log_file_dict["storage"])
        
        # Create log files
        self._log_file_dict["log_files"].update({"raw": f'{self._log_file_dict["storage"]}/RawLog.txt'})
        os.mkdir(self._log_file_dict["log_files"]["raw"])

        for key,value in self._main_config_dict["log"].items():
            if value == True:
                self._log_file_dict["log_files"].update({key: f'{self._log_file_dict["storage"]}/{key}.txt'})
                os.mkdir(self._log_file_dict["log_files"][key])

        # Go to ADB connect state
        #self._go_to_next_state(MainStateEnum.MAIN_STATE_ADB_CONNECT)
        
        # Go to dmesg state manager
        self._go_to_next_state(MainStateEnum.MAIN_STATE_DMESG)
        return
    
    def _adb_connect_state_manager(self): # TODO ELIMINARE !?
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
                
                # Run fake command to know if adb shell works
                res = subprocess.run("adb shell date", text=True, capture_output=True)
                
                if res.stdout:
                    timer.stop()
                    break
                else:
                    timer.reset()

                count += 1
        
        if not res.stdout:            
            sys.stdout.write("\033[K")
            print("No Device Found", end="\r")            

        else:
            sys.stdout.write("\033[K")
            print ("SX5 Found", end = "\r")               
        
        # Go to Open Record App State
        self._go_to_next_state(MainStateEnum.MAIN_STATE_DMESG)
        
        return

    def _dmesg_state_manager(self):
        """"""
        dmesg = ""

        try:            
            dmesg = self._sx5.read_dmesg()
        except exceptions.TcpTimeoutException: 
            # Go to stop state
            self._go_to_next_state(MainStateEnum.MAIN_STATE_STOP)
        else:
            # Update raw log file
            raw_log = open(file=self._log_file_dict['log_files']['raw'], mode='a', newline='')
            raw_log.write(dmesg)
            raw_log.close()

            # Update single log files            
            for keyword in self._log_file_dict['log_files'].keys():
                # Open log file that correspond to keyword
                log_file = open(file=self._log_file_dict['log_files'][keyword], mode='a', newline='')

                for line in raw_log.split('\n'):
                    if line.find(keyword):
                        # If there is the keyword, update the log with the corresponding line
                        log_file.write(line)
                        
                # Close the log file
                log_file.close()
                    
        return

    def _stop_state_manager(self):
        """"""
        self._store_last_state()
        return
    
    def _exit_state_manager(self):
        """"""
        return
    
    def _main_state_machine_manager(self):
        """"""
        # Get function from dictionary
        fun = self._main_state_fun_dict.get(self._main_state)

        # Execute function
        fun()

        return

    # ************************************************ #
    # **************** Public Methods **************** #
    # ************************************************ #

    def init(self):
        """"""
        # Initialize Colorama library
        cm.init(autoreset=True)

        # Parse config file 
        self._parse_config_file()
        
        self._main_state = MainStateEnum.MAIN_STATE_INIT
        self._last_main_state = MainStateEnum.MAIN_STATE_INIT
    
        return

    def run(self):
        """ Main Application """
        
        # Init
        self._init_state_manager()
        
        while not (self._main_state == MainStateEnum.MAIN_STATE_STOP and
                   self._last_main_state == MainStateEnum.MAIN_STATE_STOP):
            
            if self._global_timer.elapsed_time_s() >= 1:
                # Store the last state machine state
                #self._store_last_state()

                # Run state machine at current state
                self._main_state_machine_manager()
      
if __name__ == "__main__":    
    test = Main()
    test.init()
    test.run()
