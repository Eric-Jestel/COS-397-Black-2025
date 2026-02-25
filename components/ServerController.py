# This is the server controller

# import Sample

import requests
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime, timezone


class ServerController:
    """
    Communicates with the Inter Chem Net Server
    """

    def __init__(self, file_dir):

        load_dotenv()

        self.api_key = os.getenv("ICN_PRIVATE_API_KEY")
        self.api_url = (
            "https://interchemnet.avibe-stag.com/spectra/api/{link_end}?key={api_key}"
        )

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

        url_input = self.api_url.format(
            link_end="connection-check", api_key=self.api_key
        )

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
            # server returns ISO datetime string for expiresOn
            self.UUID = response.json().get("sessionUUID")
            self.UUID_expiry = response.json().get("expiresOn")
            self.user = username
            return {"expiresOn": self.UUID_expiry}
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
        return self.validate()

    def validate(self) -> bool:
        """
        Validate session: three clauses
          1) session UUID exists (non-zero/non-empty)
          2) expiry time is in the future
          3) username exists

        Returns True if all clauses pass.
        """
        # 1: session UUID
        if not self.UUID:
            return False

        # 3: username exists
        if not self.user:
            return False

        # 2: expiry in future
        if not self.UUID_expiry:
            return False
        try:
            exp = datetime.fromisoformat(self.UUID_expiry.replace("Z", "+00:00"))
            return datetime.now(timezone.utc) < exp
        except Exception:
            return False

    def send_all_data(self):
        """
        Attempts to send all unsent data to ICN

        Returns:
            list of filenames and boolean indicating if sent
        """

        successes = []

        p = Path(self.file_dir)
        if not p.exists():
            return successes

        for filepath in p.iterdir():
            if not filepath.is_file():
                continue
            if filepath.suffix.lower() not in {".csv", ".txt"}:
                continue

            stem = filepath.stem
            parts = stem.rsplit("_", 2)
            if len(parts) != 3:
                continue
            owner, dt_str, flag = parts
            if flag.lower() != "unsent":
                continue

            sent = False
            if self.user != owner or not self.is_logged_in():
                # attempt to login as that owner
                self.login(owner)

            if self.send_data(str(filepath)):
                # rename to sent
                new_name = f"{owner}_{dt_str}_sent{filepath.suffix}"
                filepath.rename(filepath.with_name(new_name))
                sent = True

            successes.append((filepath.name, sent))

        return successes

    def send_data(self, samplePath):
        """
        Converts a sample to a file and sends all the unsent data to ICN

        Args:
            samplePath (String): The path to the sample that is being sent to ICN

        Returns:
            Boolean: True if it successful send all unsent data
        """

        # ensure logged in and session valid
        if not self.is_logged_in():
            return False

        parsed = self.parse_sample(samplePath)
        if not parsed:
            return False

        data_key = parsed.get("datetime")
        data_array = parsed.get("data", [])

        url_input = self.api_url.format(
            link_end="instrument_data_upload", api_key=self.api_key
        )

        json_input = {
            "sessionUUID": self.UUID,
            "dataKey": data_key,
            "dataArray": data_array,
        }

        try:
            response = requests.post(url_input, json=json_input)
            if response.json().get("success"):
                return True
        except Exception:
            return False

        return False

    def parse_sample(self, sampleName):
        """
        Converts a sample to a JSON object that can be sent to ICN

        Args:
            sampleName (String): The name of the sample that is being converted

        Returns:
            JSON: The JSON object that represents the sample
        """

        # sampleName is filename relative to file_dir
        p = Path(self.file_dir) / sampleName
        if not p.exists():
            return None

        stem = p.stem
        parts = stem.rsplit("_", 2)
        if len(parts) != 3:
            return None
        owner, dt_str, flag = parts

        # validate datetime
        try:
            _ = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except Exception:
            return None

        ranges = []
        settings = {}
        data = []

        with open(p, "r", encoding="utf-8") as f:
            for raw in f:
                # do not strip fixed-width positions; only remove trailing newline
                line = raw.rstrip("\n")
                if not line.strip():
                    continue
                # tag is the first token before a space
                parts = line.split(" ", 1)
                tag = parts[0].upper()
                rest = parts[1] if len(parts) > 1 else ""

                if tag == "SETTING":
                    # SETTING {32-char name}{1 space}{32-char value}
                    name_field = rest[0:32]
                    # skip the single space at position 32
                    value_field = rest[33 : 33 + 32] if len(rest) >= 33 else rest[32:]
                    name = name_field.rstrip()
                    value = value_field.rstrip()
                    if name:
                        settings[name] = value

                elif tag == "DATA":
                    # DATA {12-char wavelength}{1 space}{13-char absorbance}
                    wav_field = rest[0:12]
                    abs_field = rest[13 : 13 + 13] if len(rest) >= 13 else rest[12:]
                    try:
                        wav = float(wav_field.strip())
                    except Exception:
                        continue
                    try:
                        absv = float(abs_field.strip())
                    except Exception:
                        continue
                    data.append({"wavelength": wav, "absorbance": absv})

                elif tag == "RANGE":
                    # RANGE {12-char low}{1 space}{12-char high}{1 space}{4-char num}
                    low_field = rest[0:12]
                    high_field = rest[13 : 13 + 12] if len(rest) >= 25 else rest[12:]
                    num_field = rest[26   26 + 4] if len(rest) >= 30 else rest[24:]
                    try:
                        low = float(low_field.strip())
                    except Exception:
                        low = None
                    try:
                        high = float(high_field.strip())
                    except Exception:
                        high = None
                    try:
                        num = int(num_field.strip()) if num_field.strip() else None
                    except Exception:
                        num = None
                    ranges.append({"low": low, "high": high, "num": num})

                else:
                    # Unknown tag — attempt to parse whitespace-separated numeric pair
                    tokens = [t for t in line.split() if t]
                    if len(tokens) >= 2:
                        try:
                            wav = float(tokens[0])
                            absv = float(tokens[1])
                            data.append({"wavelength": wav, "absorbance": absv})
                        except Exception:
                            pass

        return {
            "sampleID": stem,
            "owner": owner,
            "datetime": dt_str,
            "ranges": ranges,
            "settings": settings,
            "data": data,
        }
