# This is the system controller
#import User_Interface, Instrument Controller and Server Controller
#from User_Interface import main.py ?????
import InstrumentController
import ServerController
#Need necessary functions such as run test
def clicked(function): #IN PROGRESS
    match function:
        case "startUp":
            #Loop to make sure startup is finished before moving on
            startUpComplete = False
            while startUpComplete == False:
                #verify machine connection
                machineConnection = InstrumentController.setup()
                if machineConnection == True:
                    #verify server connection
                    serverConnection = ServerController.connect()
                    if serverConnection == True:
                        print("Connected")
                        startUpComplete = True
                    else:
                        print("Please make sure the device is connected to the internet and the interchem net is operational")
                else:
                    print("Please make sure the instrument is plugged in and turned on")
            print("starting up")
            return False
        case "signIn":
            #verify connection to ICN
            #send information to server controller to sign in
            print("signing in")
            return False
        case "runLabMachine": 
            #runs the lab machine
            #while running
            #should get running data
            #need to send the text file to UI -- Need to get variable from Alex
            #Once data is fully processed send the JSON file to the Server Controller to be sent to the InterChemNet
            print("not stopped")
            return False
        case "stopProgram":
            #sends instructions for the Server controller to disconnect
            #sends instructions for the Instrument Controller to shut down the machine
            print("stopped")
            return True
        case "":
            #do nothing :D
            print("not stopped")
            return False
        case _:
            print("Please enter a valid argument. function string does not have an accepted string")
            return False

#def runLabMachine(parameters): #NOT DONE
    #parameters
    #sends instructions to machine to run test
    #return

#def getRunData(): #NOT DONE DO ONE THING AT A TIME DAMNIT. figure out additional needs later...
    #with open("ExampleData.txt") as data:
    #    lineData = data.readlines()
    #return lineData

#def sendData():
    #needs to be able to send the data to the server controller
    #data = 0 #need to put in JSON file from IC
    #Need to send data to server controller
    #return

#def stopProgram(parameters): #NOT DONE
    #stops the program and closes window
    #tells server controller to disconnect
    #tells UI to shutdown
    #parameters
    #return True

#main function
def main():
    endProgram = False
    function = ""
    endProgram = clicked(function)
    while endProgram != True:
        #checks for what is pressed
        function = input("Please enter:\n runLabMachine\n or stopProgram\n Or type nothing\n   Answer: ")
        endProgram = clicked(function)
        
    return 
main()