from brukeropus import Opus
# import os


# need a class
class InstrumentControllerOpus:
    # need the opus machine to be instantiated
    def __init__(self):
        # needs to connect to opus
        self.opus = Opus()
        self.blankPath = None
    # ------------------------------------------------------------------------------------------------------------------------------------------

    def getBlank(self):
        # gets a reference sample aka a blank from the machine
        print("Taking Blank")
        self.opus.measure_ref()
        # TA can set name so fix later
        self.opus.save_ref(r"C:\Users\Public\Documents\Bruker\Opus_8.8.4\Data\RefBlank.0")

    # TA can change so fix later
    def loadBlank(self, filepath=r"C:\Users\Public\Documents\Bruker\Opus_8.8.4\Data\RefBlank.0"):
        # uses the filepath to load the blank
        self.opus.open(filepath)
