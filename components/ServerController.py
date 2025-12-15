# This is the server controller

import Sample

class ServerController:
    """
    Communicates with the Inter Chem Net Server
    """

    user = None


    def connect(self):
        """
        Connects the controller to ICN

        Returns:
            Boolean: True if successful
        """
        return True


    def login(self, username):
        """
        Attempts to login the user with that username

        Args:
            username (String): the username of the user currently accessing ICN

        Returns:
            Boolean: True if successful
        """
        self.user = username
        return True
    

    def logout(self):
        """
        Logs out a user

        Returns:
            Boolean: True if successful
        """
        self.user = None
        return True
    
    
    def is_logged_in(self):
        """
        Checks if a user is logged in

        Returns:
            Boolean: True if a user is logged in
        """
        return self.user != None


    def send_all_data(self):
        """
        Attempts to send all unsent data to ICN

        Returns:
            Boolean: True if successful
        """
        return True
    

    def send_data(self, sample):
        """
        Converts a sample to a file and sends all the unsent data to ICN

        Args:
            sample (Sample): The sample that is being sent to ICN

        Returns:
            Boolean: True if it successful send all unsent data
        """
        return self.send_all_data()
    