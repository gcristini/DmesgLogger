
import sys
import os
import subprocess
import time
import json
from Libraries.Timer import Timer

class MainStateEnum:
    MAIN_STATE_INIT = "init"    
    MAIN_STATE_DMESG_FILTER = "dmesg_filter"
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
        
        self._main_state_fun_dict = {
            MainStateEnum.MAIN_STATE_INIT: self._init_state_manager,
            MainStateEnum.MAIN_STATE_DMESG_FILTER: self._dmesg_filter_state_manager,
            MainStateEnum.MAIN_STATE_STOP: self._stop_state_manager,
            MainStateEnum.MAIN_STATE_EXIT: self._exit_state_manager
        }
       
        self._main_state: None
        self._last_main: None
        
        return


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
        with open("DmesgFilterConfig.json") as json_file:
            self._main_config_dict = json.load(json_file)
            self._main_config_dict['file']['folder_path']=self._main_config_dict['file']['folder_path'].replace('\\', '/')

        return

    @staticmethod
    def _get_file_length(fname):
        with open(file=fname, mode='r') as f:
            for i, l in enumerate(f):
                pass

        return i + 1

    # ------------------ STATE MACHINE ------------------ #
    def _go_to_next_state(self, state):
        """"""
        # Store last state
        self._store_last_state()

        # Go to next state
        self._main_state = state

        return

    def _store_last_state(self):
        """"""
        # Store last state
        self._last_main_state = self._main_state

        return

    def _init_state_manager(self):
        """"""                  
        # Go to dmesg filter state
        self._go_to_next_state(MainStateEnum.MAIN_STATE_DMESG_FILTER)

        return    
       
    def _dmesg_filter_state_manager(self):
        """"""        
        #print (self._main_config_dict)
        input_dmesg_name = self._main_config_dict['file']['folder_path'] + self._main_config_dict['file']['input_file']
        output_dmesg_name = self._main_config_dict['file']['folder_path'] + self._main_config_dict['file']['output_file']
        res = ""

        if os.path.isfile(output_dmesg_name):
            res = input (f'{self._main_config_dict["file"]["output_file"]} already exist: subscribed? [y/n] ')

        if (res.upper() == "Y" or not os.path.isfile(output_dmesg_name)):
            
            # Get lenth of file
            lines_tot = self._get_file_length(input_dmesg_name)

            with open (file=input_dmesg_name, mode='r') as input_dmesg, open(file=output_dmesg_name, mode='w', newline='\n') as output_dmesg:
                line_counter = -1
                progressbar_timer = Timer()
                progressbar_timer.start()
                while True:
                    line_counter +=1
                    # Update progress bar every 100ms
                    if progressbar_timer.elapsed_time_ms() >= 100:
                        progress = round(100*line_counter/lines_tot)
#                        progress = 11
                        #print ('Processing... [' + '='*progress +   ' '*(100-progress) + '] ' + str(round(progress)) + '%', end='\r')
                        print ('Processing... [' + chr(5)*progress + ' '*(100-progress) + ']'+ str(round(progress)) + '%', end='\r')
                        progressbar_timer.reset()

                    # Read line from input dmesg
                    line = input_dmesg.readline()
                    
                    # Looking for allowed keyword
                    for allowed_key in self._main_config_dict["keywords"]["include"]:
                        # If one of the allowed key is in the line...
                        if line.find(allowed_key) != -1:
                            # Looking for denied keywordsy
                            for count, denied_key in enumerate(self._main_config_dict["keywords"]["exclude"]):
                                if line.find(denied_key) != -1:
                                    break
                                elif (line.find(denied_key) == -1 and count == (len (self._main_config_dict["keywords"]["exclude"]) -1)):
                                    output_dmesg.writelines(line)
                                else:
                                    pass

                            break
                    
                    # Exit when the input dmesg has been read
                    if not line:
                        break
            
            # Go to stop state
            self._go_to_next_state(MainStateEnum.MAIN_STATE_STOP)
            
        elif res.upper() == "N":
            # Go to exit state
            self._go_to_next_state(MainStateEnum.MAIN_STATE_EXIT)
        else:
            pass
        
        return

    def _stop_state_manager(self):
        """"""
        print (f'\n\nFiltered dmesg saved in {self._main_config_dict["file"]["folder_path"] + self._main_config_dict["file"]["output_file"]}')

        # Store last state
        self._store_last_state()
        return
    
    def _exit_state_manager(self):
        """"""
        input("\nPress enter to exit")

        # Exit from program
        exit(1)
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
        # Parse config file 
        self._parse_config_file()

        # Variables initialization
        self._main_state = MainStateEnum.MAIN_STATE_INIT
        self._last_main_state = MainStateEnum.MAIN_STATE_INIT
    
        return

    def run(self):
        """ Main Application """
        
        # Init
        self._init_state_manager()
        
        while not (self._main_state == MainStateEnum.MAIN_STATE_STOP and
                   self._last_main_state == MainStateEnum.MAIN_STATE_STOP):
            
                # Run state machine at current state
                self._main_state_machine_manager()
        
        self._exit_state_manager()
      
if __name__ == "__main__":    
    test = Main()
    test.init()
    test.run()
