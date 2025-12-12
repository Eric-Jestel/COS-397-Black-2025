# This is the UI

import tkinter as TK
from tkinter import *

def create_setup_page():
    #root
    setup = Tk()
    setup.title("Setup Window") #sets the top title of the window
    #setup.geometry("500x700") #sets the height and width of the window
    #buttons call other functions
    takeSamplePopupButton = Button(setup, #set to the Tk page
                                   text="Take Sample", #What the button says on it
                                   command=create_take_sample_popup, #What command gets used on click
                                   activebackground="green", #What color the button is when pressed
                                   activeforeground="black", #What color the Text is when unpressed
                                   bg="black", #background color unpressed
                                   fg="white", #Text Color unpressed
                                   font=("Times New Roman", 12), #Font and size
                                   )
    takeSamplePopupButton.pack()
    setup.mainloop()
    print("")

def create_instrument_page():
    print("")

def create_advanced_settings():
    print("")

def create_take_sample_popup():
    samplePopupWindow = Toplevel()
    #<NEEDS BUTTON TO GIVE INSTRUCTIONS TO THE CONTROLLER>
    text=Label(samplePopupWindow, text="Testing") #creates the text
    text.pack() #packs the text into the popup
    testButton = Button(samplePopupWindow, 
                        text="Press to close window",
                        command=samplePopupWindow.destroy)
    testButton.pack()
    print("")

def create_sample_taken_popup():
    print("")

def create_resetting_popup():
    print("")
create_setup_page()
