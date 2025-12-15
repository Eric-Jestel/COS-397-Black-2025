# This is the Instrument Controller

import Sample

class InstrumentController:
    """
    Communicates with the instrument
    """

    def setup(self):
        """
        Sets up the instrument
        """
        return


    def take_blank(self, filename):
        """
        Sends a command to the instrument to take a blank sample and saves it to a file

        Args:
            filename (String): the name of the file that the blank will be saved to

        Returns:
            Boolean: True if successful
        """
        return True
    

    def set_blank(self, filename):
        """
        Sets the blank that the machine will test the generated samples against

        Args:
            filename (String): the name of the file that the holds the blank's data

        Returns:
            Boolean: True if successful
        """
        return True


    def take_sample(self):
        """
        Sends a command to the instrument to take a sample and converts the sample to a Sample object

        Returns:
            Sample: the sample that the instrument collected
        """
        return Sample("test", "uv-vis", [2.0,2.5,3.0,2.5], 0.1)
    
    
    def shutdown(self):
        """
        Shuts the instrument down

        Returns:
            Boolean: True if successful
        """
        return True
    