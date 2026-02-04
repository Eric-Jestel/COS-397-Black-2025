# This is the system controller

from InstrumentController import InstrumentController
from ServerController import ServerController


class SystemController:

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
