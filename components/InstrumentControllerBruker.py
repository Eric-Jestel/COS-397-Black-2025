from brukeropus import Opus

# need a class
class InstrumentControllerOpus:
    # need the machine instantiated
    def __init__(self):
        # need to connect to opus software
        self.opus = Opus()
        self.blankPath = None

    def getBlank(self):
        # gets a reference sample aka a blank from the machine
        self.opus.measure_ref()
        self.opus.save_ref("C:\Users\Public\Documents\Opus_8.8.4\Data\RefBlank.0") # TA can change this so fix later
    
    def loadBlank(self, filepath):
        #uses the filepath to load the blank
        self.opus.open(filepath)
    