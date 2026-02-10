# This is the system controller
#import User_Interface, Instrument Controller and Server Controller
#from User_Interface import main.py ?????
from InstrumentController import InstrumentController
from ServerController import ServerController
#Need necessary functions such as run test
def clicked(function, ServController, InstController): #IN PROGRESS
    match function:
#------------------------------------------------------------------------------------------------------------------------------------------
        case "startUp":
            startUp(ServController, InstController)
            return False
#------------------------------------------------------------------------------------------------------------------------------------------
        case "signIn":
            signIn(ServController)
            return False
#------------------------------------------------------------------------------------------------------------------------------------------
        case "signOut":
            signOut(ServController)
            return False
#------------------------------------------------------------------------------------------------------------------------------------------
        case "takeBlank":
            #verify the InstrumentController is connected
            #no function yet
            #take blank
            Blank = InstController.take_blank("Test.txt")
            #send blank to UI -- Need variable from Alex!
            return False
#------------------------------------------------------------------------------------------------------------------------------------------
        case "setBlank":
            #this dosn't really need its own function since it is defined in the Instrument Controller
            InstController.set_blank("Test.txt")
            return False
#------------------------------------------------------------------------------------------------------------------------------------------
        case "runLabMachine": 
            #runs the lab machine
            #while running it should get running data
            #need to send the text file to UI -- Need to get variable from Alex
            #Once data is fully processed send the JSON file to the Server Controller to be sent to the InterChemNet
            if ServController.is_logged_in():
                ServController.send_data("Test")
            print("not stopped")
            return False
#------------------------------------------------------------------------------------------------------------------------------------------
        case "stopProgram":
            stopProgram(ServController, InstController)
            return True
#------------------------------------------------------------------------------------------------------------------------------------------
        case "":
            #do nothing :D
            print("not stopped")
            return False
#------------------------------------------------------------------------------------------------------------------------------------------
        case _: #NOT DONE
            print("Please enter a valid argument. Function hard coded string does not have an accepted string")
            return False
#------------------------------------------------------------------------------------------------------------------------------------------
class SystemController:
    #I need variables

    #------------------------------------------------------------------------------------------------------------------------------------------
    def startUp(self, ServController, InstController):
        #Loop to make sure startup is finished before moving on
        startUpComplete = False
        while startUpComplete == False:
            #verify machine connection
            if InstController.setup():
                #verify server connection
                if ServController.connect():
                    print("Connected")
                    startUpComplete = True
                else:
                    print("Please make sure the device is connected to the internet and the interchem net is operational")
                    useless = input("Press 'Enter' to continue: ")
            else:
                print("Please make sure the instrument is plugged in and turned on")
                useless = input("Press 'Enter' to continue: ")
        print("starting up")
        return True
    #------------------------------------------------------------------------------------------------------------------------------------------
    def signIn(self, ServController, username):
        #verify connection to ICN
        if ServController.connect():
            #send information to server controller to sign in
            if ServController.login(username):
                print(ServController.user + ": signing in")
                return True
            else:
                print("Please enter valid credentials")
                return False
        else:
            print("Please make sure the device is connected to the internet and the interchem net is operational")
            useless = input("Press 'Enter' to continue: ")
            return False
    #------------------------------------------------------------------------------------------------------------------------------------------
    def signOut(self, ServController):
        #check to see if anyone is logged in already
        if ServController.is_logged_in():
            ServController.logout()
    #------------------------------------------------------------------------------------------------------------------------------------------

    #------------------------------------------------------------------------------------------------------------------------------------------
    def runLabMachine(self, ServController, InstController):
        #sends instructions to machine to run test
        data = InstController.take_sample()
        #sends data to UI somehow and send data to server controller to send to the ICN
        ServController.send_data(data)
    #------------------------------------------------------------------------------------------------------------------------------------------
    def stopProgram(self, ServController, InstController):
        #sends instructions for the Server controller to disconnect
        if ServController.is_logged_in():
            ServController.logout()
        #sends instructions for the Instrument Controller to shut down the machine
        InstController.shutdown()
        print("stopped")
    #------------------------------------------------------------------------------------------------------------------------------------------
#error code stuffs
'''
1) Machine is not connecting
2) Server is not connecting
3) No blank to set
3) 
'''

#main function
def main():
    endProgram = False
    function = ""
    ServController = ServerController()
    InstController = InstrumentController()
    endProgram = clicked(function, ServController, InstController)
    while endProgram != True:
        #checks for what is pressed
        function = input("Please enter:\n runLabMachine\n or stopProgram\n Or type nothing\n   Answer: ")
        endProgram = clicked(function, ServController, InstController)
        
    return 
main()