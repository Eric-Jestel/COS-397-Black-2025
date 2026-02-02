# This is the system controller
import User_Interface

#Need necessary functions such as run test
#AHHHH THIS IS BIG TEST
def clicked(function, endProgram): #IN PROGRESS
    match function:
        #runs machine
        case "runLabMachine":
            parameters = ""
            runLabMachine(parameters)
            #while running
            #should get running data
            data = getRunData()
            #need to send the JSON file to UI -- Need to get variable from Alex
        
        #stops the checks and shuts down the program
        case "stopProgram":
            parameters = ""
            endProgram = stopProgram(parameters)
        #Does nothing because nothing was pressed
        case "":
            return False
        case _:
            print("Please enter a valid instruction")
            return False

def runLabMachine(parameters): #NOT DONE
    parameters
    #sends instructions to machine to run test
    return

def getRunData(): #NOT DONE DO ONE THING AT A TIME DAMNIT. figure out additional needs later...
    with open("ExampleData.txt") as data:
        lineData = data.readlines()
    return lineData

def sendData():
    #needs to be able to send the data to the server controller
    data = 0 #need to put in JSON file from IC
    #Need to send data to server controller
    return

def stopProgram(parameters): #NOT DONE
    #stops the program and closes window
    #tells server controller to disconnect
    #tells UI to shutdown
    parameters
    return True

#main function
def main():
    endProgram = False
    function = ""
    while endProgram != True:
        #checks for what is pressed
        endProgram = clicked(function)
    return 
main()