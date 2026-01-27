# This is the system controller


#Need necessary functions such as run test

def clicked(function):
    match function:
        #runs machine
        case "runLabMachine":
            parameters = ""
            runLabMachine(parameters)
        #stops the checks and shuts down the program
        case "stopProgram":
            parameters = ""
            stopProgram(parameters)
        #Does nothing because nothing was pressed
        case "":
            return
        case _:
            return print("Please enter a valid instruction")

def runLabMachine(parameters):
    parameters
    #sends instructions to machine to run test
    return

def stopProgram(parameters):
    parameters
    #stops the program and closes window
    return True

#main function
def main():
    endProgram = False
    function = ""
    while endProgram != True:
        #checks for what is pressed
        clicked(function)
    return 
main()