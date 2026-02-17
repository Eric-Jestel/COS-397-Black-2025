# This is the system controller

from InstrumentController import InstrumentController
from ServerController import ServerController

#------------------------------------------------------------------------------------------------------------------------------------------
class SystemController:
    #I need variables
    ServController = ServerController()
    InstController = InstrumentController()
    #------------------------------------------------------------------------------------------------------------------------------------------
    def startUp(self):
        #verify machine connection
        InstConn = self.InstController.setup()
        if InstConn == True:
            #verify server connection
            ServConn = self.ServController.connect()
            if ServConn == True:
                return 111
            else:
                return 110
        else:
            return 100
    #------------------------------------------------------------------------------------------------------------------------------------------
    def signIn(self, username):
        #verify connection to ICN
        if self.ServController.connect():
            #send information to server controller to sign in
            loggedIn=self.ServController.login(username)
            if loggedIn==True:
                return 222
            else:
                return 220
        else:
            return 110
    #------------------------------------------------------------------------------------------------------------------------------------------
    def signOut(self):
        #check to see if anyone is logged in already
        if self.ServController.is_logged_in():
            if self.ServController.logout():
                return 333
            else:
                return 330
        else:
            return 300
    #------------------------------------------------------------------------------------------------------------------------------------------
    def runLabMachine(self):
        #verify instrument connection
        if self.InstController:
            #sends instructions to machine to run test
            data = self.InstController.take_sample()
            if data:
                #verify server connection
                if self.ServController.connect():
                    #sends data to UI somehow and send data to server controller to send to the ICN
                    self.ServController.send_data(data)
                    return 440, data
                else:
                    return 110
            else:
                return 400
        else:
            return 100
    #------------------------------------------------------------------------------------------------------------------------------------------
    def takeBlank(self):
        #verify instrument connection
        if self.InstController:
            #sends instructions to machine to run test
            data = self.InstController.take_sample()
            if data:
                #send data to UI to hold onto for setting the blank
                return 444, data
            else:
                return 400
        else:
            return 100
    #------------------------------------------------------------------------------------------------------------------------------------------
    def setBlank(self, data):
        #verify instrument connection
        if self.InstController:
            #sends instructions to machine to run test
            data = self.InstController.take_sample()
            if data:
                #send instructions to machine to set data
                set = self.InstController.set_Blank(data)
                if set == True:
                    return 555
                else:
                    return 550
            else:
                return 400
        else:
            return 100
    #------------------------------------------------------------------------------------------------------------------------------------------
    def stopProgram(self):
        #verify the server controller is connected and logged in
        if self.ServController.connect():
            if self.ServController.is_logged_in():
                #sends instructions for the Server controller to disconnect
                self.ServController.logout()
            #verify instrument connection
            if self.InstController:
                #sends instructions for the Instrument Controller to shut down the machine
                self.InstController.shutdown()
                return 666
            else:
                return 100
        else:
            return 110
    #------------------------------------------------------------------------------------------------------------------------------------------
#error code stuffs
'''
All of this is subject to change
Preabmle = three same digits (e.g. 111) mean that it is good to go
1) 100 = Machine is not connecting
2) 110 = Server is not connecting
3) 220 = Not a valid Account
4) 330 = User not logged in
5) 400 = No data :(
6) 550 = No blank to set
'''
#Info needed
'''
I need a way to verify server connectivity (ping it)
I need a way to verify machine connectivity (maybe ping it?)
When running the machine is there really no possible way to send information to and from the instrument controller to the machine controller?

'''




class SystemControllerSample:

    instCon = InstrumentController()
    servCon = ServerController()
    samples = []

    def setup(self):
        """
        Sets up the instrument and server controllers

        Returns:
            Boolean: True if successful
        """
        return self.instCon.setup() and self.servCon.connect()

    def take_blank(self, filename):
        """
        Takes a blank sample and saves it to a file

        Args:
            filename (String): The name of the file that the blank sample is saved to

        Returns:
            Boolean: True if successful
        """
        return self.instCon.take_blank(filename)

    def set_blank(self, filename):
        """
        Sets the blank that the instrument will compare samples against

        Args:
            filename (String): the name of the blank file

        Returns:
            Boolean: True if successful
        """
        return self.instCon.set_blank(filename)

    def take_sample(self):
        """
        Takes a sample and sends it to ICN

        Returns:
            Boolean: True if successful
        """
        if not self.servCon.is_logged_in():
            return False
        newSample = self.instCon.take_sample()
        self.sample.append(newSample)
        return self.servCon.send_data(newSample)

    def login_user(self, username):
        """
        Logs in a user with the given username

        Args:
            username (string): the username of the user

        Returns:
            Boolean: True if successful
        """
        return self.servCon.login(username)

    def logout_user(self):
        """
        Logs out the user currently logged in

        Returns:
            Boolean: True if successful
        """
        self.samples = []
        return self.servCon.logout()

    def display_data(self):
        """
        Displays all the samples the user has currently taken
        """
        return

    def shutdown(self):
        """
        Shuts down the instrument and sends all unsent data to ICN

        Returns:
            Boolean: True if it successfuly sent all unsent data
        """
        self.logout_user()
        self.instCon.shutdown()
        return self.servCon.send_all_data()
