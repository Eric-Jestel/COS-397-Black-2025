# This is the Instrument Controller



try:
    from Sample import Sample
except ImportError:
    from components.Sample import Sample


import json
import time
import uuid
import winreg
from datetime import datetime
from pathlib import Path


class InstrumentController:
    """
    Communicates with the instrument
    """

    ROOT = r"Software\GenChem\CaryBridge"
    QUEUE_KEY = ROOT + r"\Queue"
    PARAMS_KEY = ROOT + r"\Params"
    STATE_KEY = ROOT + r"\State"
    POLL_INTERVAL_S = 0.1
    TIMEOUT_S = 60.0

    def __init__(self):
        self.blank_file = ""
        self.sample_wavelength_nm = 260
        self.scan_start_nm = 600
        self.scan_stop_nm = 500

    @staticmethod
    def _ensure_key(subkey: str) -> None:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, subkey)

    @classmethod
    def _reg_set(cls, subkey: str, name: str, value: str) -> None:
        cls._ensure_key(subkey)
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, subkey, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)

    @staticmethod
    def _reg_get(subkey: str, name: str, default: str = "") -> str:
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, subkey, 0, winreg.KEY_QUERY_VALUE
            ) as key:
                value, _ = winreg.QueryValueEx(key, name)
                return str(value)
        except FileNotFoundError:
            return default
        except OSError:
            return default

    @classmethod
    def _clear_mailbox(cls, reset_file_counter: bool = False) -> None:
        cls._ensure_key(cls.QUEUE_KEY)
        cls._ensure_key(cls.PARAMS_KEY)
        cls._ensure_key(cls.STATE_KEY)

        status = cls._reg_get(cls.STATE_KEY, "Status", "")
        if status.upper() == "BUSY":
            print("WARNING: ADL bridge reports Status=BUSY. Clearing mailbox anyway.")

        cls._reg_set(cls.QUEUE_KEY, "Command", "")
        cls._reg_set(cls.QUEUE_KEY, "CommandId", "")
        cls._reg_set(cls.PARAMS_KEY, "Json", "")
        cls._reg_set(cls.STATE_KEY, "ReplyId", "")
        cls._reg_set(cls.STATE_KEY, "ResultPath", "")
        cls._reg_set(cls.STATE_KEY, "Error", "")
        cls._reg_set(cls.STATE_KEY, "Status", "IDLE")

        if reset_file_counter:
            cls._reg_set(cls.STATE_KEY, "FileCounter", "0")

    @classmethod
    def _send_command(cls, command: str, params: dict) -> str:
        cmd_id = str(uuid.uuid4())
        cls._reg_set(cls.PARAMS_KEY, "Json", json.dumps(params))
        cls._reg_set(cls.QUEUE_KEY, "CommandId", cmd_id)
        cls._reg_set(cls.QUEUE_KEY, "Command", command)
        return cmd_id

    @classmethod
    def _wait_for_reply(cls, cmd_id: str, timeout_s: float = None) -> dict:
        if timeout_s is None:
            timeout_s = cls.TIMEOUT_S

        deadline = time.time() + timeout_s
        while time.time() < deadline:
            reply_id = cls._reg_get(cls.STATE_KEY, "ReplyId", "")
            if reply_id == cmd_id:
                return {
                    "reply_id": reply_id,
                    "status": cls._reg_get(cls.STATE_KEY, "Status", ""),
                    "result_path": cls._reg_get(cls.STATE_KEY, "ResultPath", ""),
                    "error": cls._reg_get(cls.STATE_KEY, "Error", ""),
                }
            time.sleep(cls.POLL_INTERVAL_S)

        return {
            "reply_id": "",
            "status": "TIMEOUT",
            "result_path": "",
            "error": "Timed out waiting for ADL reply",
        }

    @staticmethod
    def _is_success(reply: dict) -> bool:
        status = str(reply.get("status", "")).upper()
        return status not in {"", "TIMEOUT", "ERROR", "FAILED"}

    def _send_and_wait(
        self, command: str, params: dict, timeout_s: float = None
    ) -> dict:
        cmd_id = self._send_command(command, params)
        return self._wait_for_reply(cmd_id, timeout_s=timeout_s)

    def setup(self):
        """
        Sets up the instrument
        """
        try:
            self._clear_mailbox(reset_file_counter=False)
            self._ensure_key(self.QUEUE_KEY)
            self._ensure_key(self.PARAMS_KEY)
            self._ensure_key(self.STATE_KEY)
            reply = self._send_and_wait(
                "PING", {"ts": datetime.now().astimezone().isoformat()}, timeout_s=10.0
            )
            return self._is_success(reply)
        except OSError:
            return False

    def changeParams(self, input_params: dict):
        """
        Changes the parameters of the instrument

        Args:
            input_params (dict): a dictionary of parameters to change. Valid keys:
                TBD - depends on what the instrument takes

        Returns:
            Boolean: True if successful
        """

        params_file = Path(__file__).parent / "storedParams.txt"

        # Load existing params if file exists
        existing_params = {}
        if params_file.exists():
            with open(params_file, "r") as f:
                for line in f:
                    key, value = line.strip().split(",", 1)
                    existing_params[key] = value

        # Update with new params
        existing_params.update(input_params)

        # Write all params back
        with open(params_file, "w") as f:
            for key, value in existing_params.items():
                f.write(f"{key},{value}\n")

        return True

    def take_blank(self, filename):
        """
        Sends a command to the instrument to take a blank sample and saves it to a file

        Args:
            filename (String): the name of the file that the blank will be saved to

        Returns:
            Boolean: True if successful
        """
        out_target = Path(filename)
        out_target.parent.mkdir(parents=True, exist_ok=True)
        out_base = out_target.with_suffix("")

        params = {
            "start_nm": self.scan_start_nm,
            "stop_nm": self.scan_stop_nm,
            "out_base": str(out_base),
        }
        reply = self._send_and_wait("SCAN", params)
        if self._is_success(reply):
            print("Blank scan successful, result path:", reply.get("result_path"))
            self.blank_file = reply.get("result_path") or str(out_target)
            return True
        return False

    def set_blank(self, filename):
        """
        Sets the blank that the machine will test the generated samples against

        Args:
            filename (String): the name of the file that the holds the blank's data

        Returns:
            Boolean: True if successful
        """
        blank_path = Path(filename)
        if not blank_path.exists():
            return False
        self.blank_file = str(blank_path)
        return True

    def take_sample(self):
        """
        Sends a command to the instrument to take a sample and converts the sample to a Sample object

        Returns:
            Sample: the sample that the instrument collected
        """
        params = {"wavelength_nm": self.sample_wavelength_nm}
        if self.blank_file:
            params["blank_file"] = self.blank_file

        reply = self._send_and_wait("READ", params)
        if not self._is_success(reply):
            return None
        sample_name = datetime.now().strftime("sample_%Y%m%d_%H%M%S")
        return Sample(sample_name, "uv-vis", [], 0.0)

    def shutdown(self):
        """
        Shuts the instrument down

        Returns:
            Boolean: True if successful
        """
        reply = self._send_and_wait("SHUTDOWN", {})
        return self._is_success(reply)

import subprocess
import time

file = ".\\COS-397-Black-2025\\components\\MailboxCheck.adl"

subprocess.Popen(file, shell=True)

print("Launched. Wait 10 seconds")
time.sleep(10)


testing = InstrumentController()

print(testing.setup())
print(testing.take_blank("test_blank.txt"))

