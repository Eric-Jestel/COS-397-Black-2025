# This is the server controller

# import Sample

import requests
from dotenv import load_dotenv
import os
import time


class ServerController:
    """
    Communicates with the Inter Chem Net Server
    """
    def __init__(self, file_dir):
        
        load_dotenv()

        self.api_key = os.getenv("ICN_PRIVATE_API_KEY")
        self.api_url = "https://interchemnet.avibe-stag.com/spectra/api/{link_end}?key={api_key}"
        
        self.user = None

        self.UUID = 0
        self.UUID_expiry = 0

        self.file_dir = file_dir



    def ping(self):
        """
        Sends a basic get request to the ICN server

        Returns:
            Boolean: True if successful
        """

        url_input = self.api_url.format(link_end="connection-check", api_key=self.api_key)

        response = requests.get(url_input)

        if response.json().get("status") == "alive":
            return True
        elif response.json().get("status") == "maintenance":
            return False
        else:
            raise Exception("Unexpected response from server: " + response.text)

    def login(self, username):
        """
        Attempts to login the user with that username

        If it passes, generates a session UUID and stores it

        Args:
            username (String): the username of the user currently accessing ICN

        Returns:
            Boolean: True if successful
        """
        # Reset info
        self.UUID = 0
        self.UUID_expiry = 0
        self.user = None
        
        url_input = self.api_url.format(link_end="user-session", api_key=self.api_key)

        json_input = {"studentUserName": username}

        response = requests.post(url_input, json=json_input)
        
        if response.json().get("success"):
            self.UUID = response.json().get("sessionUUID")
            self.UUID_expiry = response.json().get("expiresOn")
            self.user = username
            return True
        else:
            return False

    def logout(self):
        """
        Logs out a user

        Returns:
            Boolean: True if successful
        """
        self.UUID = 0
        self.UUID_expiry = 0
        self.user = None
        return True

    def is_logged_in(self):
        """
        Checks if a user is logged in

        Returns:
            Boolean: True if a user is logged in
        """
        if (self.UUID == 0):
            self.UUID = 0
            self.UUID_expiry = 0
            self.user = None
            return False
        
        if (self.UUID_expiry < time.time()):
            self.UUID = 0
            self.UUID_expiry = 0
            self.user = None
            return False

        if (self.user == None):
            self.UUID = 0
            self.UUID_expiry = 0
            self.user = None
            return False

        return True

    def send_all_data(self):
        """
        Attempts to send all unsent data to ICN

        Returns:
            list of filenames and boolean indicating if sent
        """

        successes = []

        for filename in os.listdir(self.file_dir):
            if filename.endswith(".txt") and "unsent" in filename:
                successes.append((filename, False))
                if self.send_data(os.path.join(self.file_dir, filename)):
                    new_filename = filename.replace("unsent", "sent")
                    os.rename(os.path.join(self.file_dir, filename), os.path.join(self.file_dir, new_filename))
                    successes[-1] = (filename, True)

        return successes

    def send_data(self, samplePath):
        """
        Converts a sample to a file and sends all the unsent data to ICN

        Args:
            samplePath (String): The path to the sample that is being sent to ICN

        Returns:
            Boolean: True if it successful send all unsent data
        """

        if (self.UUID_expiry < time.time()):
            return False
        if (self.user == None):
            return False
        if (self.UUID == 0):
            return False
        

        formatted = self.parse_sample(samplePath)

        dataKey = formatted.get("dataKey")

        url_input = self.api_url.format(link_end="instrument_data_upload", api_key=self.api_key)

        json_input = {"sessionUUID": self.UUID, "dataKey": dataKey, "dataArray": formatted}

        response = requests.post(url_input, json=json_input)

        if response.json().get("success"):
            return True
        return False

    def parse_sample(self, sampleName):
        """
        Converts a sample to a JSON object that can be sent to ICN

        Args:
            sampleName (String): The name of the sample that is being converted

        Returns:
            JSON: The JSON object that represents the sample
        """

        sampleID = os.path.splitext(sampleName)[0]  # Extract filename without extension
    
        with open(os.path.join(self.file_dir, sampleName), 'r') as f:
            existing_params = {}
            for line in f:
                key, value = line.strip().split(',', 1)  # Split only on the first comma
                existing_params[key] = value
        
        sampleOwner = existing_params.get("owner")
        
        return [sampleID, sampleOwner, existing_params]