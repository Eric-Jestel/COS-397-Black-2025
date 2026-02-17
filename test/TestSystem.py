# This tests the system controller

from components import SystemController 
from components import ServerController
from components import InstrumentController

#I need a system controller to test
sysCon = SystemController()

#testing that the instrument can verify connectivity
def testServerConnectivity():
    if sysCon.ServerController == True:
        return True