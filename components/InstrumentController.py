# This is the Instrument Controller


import Sample


import json
import time
import uuid
import winreg
from datetime import datetime
from pathlib import Path

# Registry mailbox base (HKCU\Software\GenChem\CaryBridge)
ROOT = r"Software\GenChem\CaryBridge"

# Subkeys (sections)
QUEUE_KEY = ROOT + r"\Queue"
PARAMS_KEY = ROOT + r"\Params"
STATE_KEY = ROOT + r"\State"

POLL_INTERVAL_S = 0.1
TIMEOUT_S = 60.0


def _ensure_key(subkey: str) -> None:
    """Create the key if it doesn't exist."""
    winreg.CreateKey(winreg.HKEY_CURRENT_USER, subkey)


def reg_set(subkey: str, name: str, value: str) -> None:
    _ensure_key(subkey)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, name, 0, winreg.REG_SZ, value)

def clear_mailbox(reset_file_counter: bool = False) -> None:
    """
    Clears the registry mailbox so there are no stale commands/replies on startup.
    NOTE: If your ADL bridge is actively processing a command, clearing may confuse it.
    """
    # Ensure keys exist
    _ensure_key(QUEUE_KEY)
    _ensure_key(PARAMS_KEY)
    _ensure_key(STATE_KEY)

    # If you want a safety warning:
    status = reg_get(STATE_KEY, "Status", "")
    if status.upper() == "BUSY":
        print("WARNING: ADL bridge reports Status=BUSY. Clearing mailbox anyway.")

    # Clear inbound (Python -> ADL)
    reg_set(QUEUE_KEY, "Command", "")
    reg_set(QUEUE_KEY, "CommandId", "")

    # Clear params
    reg_set(PARAMS_KEY, "Json", "")

    # Clear outbound (ADL -> Python)
    reg_set(STATE_KEY, "ReplyId", "")
    reg_set(STATE_KEY, "ResultPath", "")
    reg_set(STATE_KEY, "Error", "")
    reg_set(STATE_KEY, "Status", "IDLE")

    # Optional: reset the ADL logger's counter
    if reset_file_counter:
        reg_set(STATE_KEY, "FileCounter", "0")


def reg_get(subkey: str, name: str, default: str = "") -> str:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey, 0, winreg.KEY_QUERY_VALUE) as k:
            v, _ = winreg.QueryValueEx(k, name)
            return str(v)
    except FileNotFoundError:
        return default
    except OSError:
        return default


def send_command(command: str, params: dict) -> str:
    """
    Write Params, then CommandId, then Command (commit).
    Returns command_id.
    """
    cmd_id = str(uuid.uuid4())

    # Store params as JSON (keep it small; bulk data should be files)
    reg_set(PARAMS_KEY, "Json", json.dumps(params))

    # Correlate request/response
    reg_set(QUEUE_KEY, "CommandId", cmd_id)

    # Commit command LAST
    reg_set(QUEUE_KEY, "Command", command)

    return cmd_id


def wait_for_reply(cmd_id: str, timeout_s: float = TIMEOUT_S) -> dict:
    """
    Wait until State ReplyId matches cmd_id or timeout.
    Returns dict with status/result/error.
    """
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        reply_id = reg_get(STATE_KEY, "ReplyId", "")
        if reply_id == cmd_id:
            status = reg_get(STATE_KEY, "Status", "")
            result_path = reg_get(STATE_KEY, "ResultPath", "")
            error = reg_get(STATE_KEY, "Error", "")
            return {
                "reply_id": reply_id,
                "status": status,
                "result_path": result_path,
                "error": error,
            }
        time.sleep(POLL_INTERVAL_S)

    return {"reply_id": "", "status": "TIMEOUT", "result_path": "", "error": "Timed out waiting for ADL reply"}


def main():
    print("CaryBridge CLI (registry mailbox)")
    print("1=PING  2=READ(260nm)  3=SCAN(600->500)  4=SHUTDOWN  q=quit")

    clear_mailbox(reset_file_counter=False)

    # Pre-create keys (optional but helpful)
    _ensure_key(QUEUE_KEY)
    _ensure_key(PARAMS_KEY)
    _ensure_key(STATE_KEY)



    while True:
        choice = input("> ").strip().lower()
        if choice in ("q", "quit", "exit"):
            break

        if choice == "1":
            cmd = "PING"
            params = {"ts": datetime.now().astimezone().isoformat()}
        elif choice == "2":
            cmd = "READ"
            params = {"wavelength_nm": 260}
        elif choice == "3":
            cmd = "SCAN"
            out_dir = Path(r"C:\CaryBridge\out")
            out_dir.mkdir(parents=True, exist_ok=True)
            out_base = out_dir / f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            params = {"start_nm": 600, "stop_nm": 500, "out_base": str(out_base)}
        elif choice == "4":
            cmd = "SHUTDOWN"
            params = {}
        else:
            print("Enter 1, 2, 3, 4, or q.")
            continue

        cmd_id = send_command(cmd, params)
        print(f"Sent {cmd} (id={cmd_id}). Waiting...")

        reply = wait_for_reply(cmd_id)
        print(f"Reply: status={reply['status']}")
        if reply["result_path"]:
            print(f"ResultPath: {reply['result_path']}")
        if reply["error"]:
            print(f"Error: {reply['error']}")

    print("Bye.")


if __name__ == "__main__":
    main()
















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
        return Sample("test", "uv-vis", [2.0, 2.5, 3.0, 2.5], 0.1)

    def shutdown(self):
        """
        Shuts the instrument down

        Returns:
            Boolean: True if successful
        """
        return True
