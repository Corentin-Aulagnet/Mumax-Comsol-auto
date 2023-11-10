from datetime import datetime
from termcolor import colored
from enum import Enum, auto

class Debug:
    logFile = "logs"
    @staticmethod
    def Log(message,color = 'white'):
        print("{} >> ".format(datetime.today().strftime('%Y-%m-%d %H:%M:%S')) + colored("{}".format(message),color))
        with open(Debug.logFile,'a') as logs:
            logs.write("{} >> {}\n".format(datetime.today().strftime('%Y-%m-%d %H:%M:%S'),message))
            
    @staticmethod
    def LogError(message):
        print("{} >> ".format(datetime.today().strftime('%Y-%m-%d %H:%M:%S')) + colored("Error: {}".format(message),'red'))
        with open(Debug.logFile,'a') as logs:
            logs.write("{} >> Error: {}\n".format(datetime.today().strftime('%Y-%m-%d %H:%M:%S'),message))
    
    @staticmethod
    def LogWarning(message):
        print("{} >> ".format(datetime.today().strftime('%Y-%m-%d %H:%M:%S')) + colored("Warning: {}".format(message),'yellow'))
        with open(Debug.logFile,'a') as logs:
            logs.write("{} >> Warning: {}\n".format(datetime.today().strftime('%Y-%m-%d %H:%M:%S'),message))

    
