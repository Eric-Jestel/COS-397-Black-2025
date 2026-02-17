# This is the system controller
# import User_Interface, Instrument Controller and Server Controller
# from User_Interface import main.py ?????
from InstrumentController import InstrumentController
from ServerController import ServerController
# ------------------------------------------------------------------------------------------------------------------------------------------
class SystemController:
    # I need variables
    ServController = ServerController()
    InstController = InstrumentController()
    # ------------------------------------------------------------------------------------------------------------------------------------------
    def startUp(self):
        # verify machine connection
        InstConn = self.InstController.setup()
        if InstConn == True:
            # verify server connection
            ServConn = self.ServController.connect()
            if ServConn == True:
                return 111
            else:
                return 110
        else:
            return 100
    # ------------------------------------------------------------------------------------------------------------------------------------------
    def signIn(self, username):
        # verify connection to ICN
        if self.ServController.connect():
            # send information to server controller to sign in
            loggedIn=self.ServController.login(username)
            if loggedIn==True:
                return 222
            else:
                return 220
        else:
            return 110
    # ------------------------------------------------------------------------------------------------------------------------------------------
    def signOut(self):
        # check to see if anyone is logged in already
        if self.ServController.is_logged_in():
            if self.ServController.logout():
                return 333
            else:
                return 330
        else:
            return 300
    # ------------------------------------------------------------------------------------------------------------------------------------------
    def runLabMachine(self):
        # verify instrument connection
        if self.InstController:
            # sends instructions to machine to run test
            data = self.InstController.take_sample()
            if data:
                # verify server connection
                if self.ServController.connect():
                    # sends data to UI somehow and send data to server controller to send to the ICN
                    self.ServController.send_data(data)
                    return 440, data
                else:
                    return 110
            else:
                return 400
        else:
            return 100
    # ------------------------------------------------------------------------------------------------------------------------------------------
    def takeBlank(self):
        # verify instrument connection
        if self.InstController:
            # sends instructions to machine to run test
            data = self.InstController.take_sample()
            if data:
                # send data to UI to hold onto for setting the blank
                return 444, data
            else:
                return 400
        else:
            return 100
    # ------------------------------------------------------------------------------------------------------------------------------------------
    def setBlank(self, data):
        # verify instrument connection
        if self.InstController:
            # sends instructions to machine to run test
            data = self.InstController.take_sample()
            if data:
                # send instructions to machine to set data
                set = self.InstController.set_Blank(data)
                if set == True:
                    return 555
                else:
                    return 550
            else:
                return 400
        else:
            return 100
    # ------------------------------------------------------------------------------------------------------------------------------------------
    def stopProgram(self):
        # verify the server controller is connected and logged in
        if self.ServController.connect():
            if self.ServController.is_logged_in():
                # sends instructions for the Server controller to disconnect
                self.ServController.logout()
            # verify instrument connection
            if self.InstController:
                # sends instructions for the Instrument Controller to shut down the machine
                self.InstController.shutdown()
                return 666
            else:
                return 100
        else:
            return 110
    # ------------------------------------------------------------------------------------------------------------------------------------------
# error code stuffs
'''
1) 100 = Machine is not connecting
2) 110 = Server is not connecting
3) 220 = Not a valid Account
4) 330 = User not logged in
5) 400 = No data :(
6) 550 = No blank to set
'''