# This tests the system controller

from components import SystemController 

#I need a system controller to test
SystemCon = SystemController()

#testing that the instrument can verify connectivity
def testServerConnectivity():
    if SystemCon.ServerController == True:
        return True