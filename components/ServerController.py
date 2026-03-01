# This is the server controller

# import Sample
# import time

import requests
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime, timezone

try:
    from Sample import Sample
except ImportError:
    from components.Sample import Sample

print("ServerController module loaded")


class ServerController:
    """
    Communicates with the Inter Chem Net Server
    """

    def __init__(self, file_dir=None, debug: bool = False):
        print(
            f"[ServerController][RECEIVED] __init__ payload={{'file_dir': {file_dir}, 'debug': {debug}}}"
        )

        load_dotenv()

        self.debug = bool(debug)

        self.api_key = os.getenv("ICN_PRIVATE_API_KEY")
        print(
            f"[ServerController][DEBUG] Loaded ICN_PRIVATE_API_KEY: {'set' if self.api_key else 'not set'}"
        )
        self.api_url = (
            "https://interchemnet.avibe-stag.com/spectra/api/{link_end}?key={api_key}"
        )

        self.user = None

        self.UUID = 0
        self.UUID_expiry = 0

        self.file_dir = file_dir or str(Path(__file__).parent / "sample_data")
        print("[ServerController][EXECUTED] __init__ result=initialized")

    def _debug(self, message: str) -> None:
        if self.debug:
            print(f"[ServerController] {message}")

    def _print_received(self, command: str, payload=None) -> None:
        print(f"[ServerController][RECEIVED] {command} payload={payload}")

    def _print_executed(self, command: str, result=None) -> None:
        print(f"[ServerController][EXECUTED] {command} result={result}")

    def _print_tx(self, method: str, url: str, payload=None) -> None:
        print(f"[ServerController][TX] method={method}, url={url}, payload={payload}")

    def connect(self) -> bool:
        """Compatibility wrapper used by `SystemController.startUp()`."""
        self._print_received("connect")
        try:
            connected = self.ping()
            self._debug(f"connect() -> {connected}")
            self._print_executed("connect", connected)
            return connected
        except Exception as exc:
            self._debug(f"connect() exception: {exc}")
            self._print_executed("connect", False)
            return False

    def ping(self):
        """
        Sends a basic get request to the ICN server

        Returns:
            Boolean: True if successful
        """

        self._print_received("ping")
        url_input = self.api_url.format(
            link_end="connection-check", api_key=self.api_key
        )

        self._debug(f"TX GET {url_input}")
        self._print_tx("GET", url_input)

        if not self.api_key:
            self._debug("ping() missing ICN_PRIVATE_API_KEY")
            self._print_executed("ping", False)
            return False

        response = requests.get(url_input, timeout=10)
        payload = response.json()
        self._debug(f"RX status_code={response.status_code}, payload={payload}")

        if payload.get("STATUS") == "alive":
            self._print_executed("ping", True)
            return True
        elif payload.get("STATUS") == "maintenance":
            self._print_executed("ping", False)
            return False
        else:
            self._print_executed("ping", "exception")
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
        self._print_received("login", {"username": username})
        # Reset info
        self.UUID = 0
        self.UUID_expiry = 0
        self.user = None

        url_input = self.api_url.format(link_end="user-session", api_key=self.api_key)

        json_input = {"studentUserName": username}

        self._debug(f"TX POST {url_input} payload={json_input}")
        self._print_tx("POST", url_input, json_input)

        response = requests.post(url_input, json=json_input, timeout=10)
        payload = response.json()
        self._debug(
            f"RX status_code={response.status_code}, success={payload.get('success')}, user={username}"
        )

        if payload.get("success"):
            # server returns ISO datetime string for expiresOn
            self.UUID = payload.get("sessionUUID")
            self.UUID_expiry = payload.get("expiresOn")
            self.user = username
            result = {"expiresOn": self.UUID_expiry}
            self._print_executed("login", result)
            return result
        else:
            self._print_executed("login", False)
            return False

    def logout(self):
        """
        Logs out a user

        Returns:
            Boolean: True if successful
        """
        self._print_received("logout")
        self.UUID = 0
        self.UUID_expiry = 0
        self.user = None
        self._debug("logout() cleared local session")
        self._print_executed("logout", True)
        return True

    def is_logged_in(self):
        """
        Checks if a user is logged in

        Returns:
            Boolean: True if a user is logged in
        """
        self._print_received("is_logged_in")
        result = self.validate()
        self._print_executed("is_logged_in", result)
        return result

    def validate(self) -> bool:
        """
        Validate session: three clauses
          1) session UUID exists (non-zero/non-empty)
          2) expiry time is in the future
          3) username exists

        Returns True if all clauses pass.
        """
        self._print_received(
            "validate",
            {
                "has_uuid": bool(self.UUID),
                "has_user": bool(self.user),
                "has_expiry": bool(self.UUID_expiry),
            },
        )
        # 1: session UUID
        if not self.UUID:
            self._print_executed("validate", False)
            return False

        # 3: username exists
        if not self.user:
            self._print_executed("validate", False)
            return False

        # 2: expiry in future
        if not self.UUID_expiry:
            self._print_executed("validate", False)
            return False
        try:
            exp = datetime.fromisoformat(self.UUID_expiry.replace("Z", "+00:00"))
            valid = datetime.now(timezone.utc) < exp
            self._print_executed("validate", valid)
            return valid
        except Exception:
            self._print_executed("validate", False)
            return False

    def send_all_data(self):
        """
        Attempts to send all unsent data to ICN

        Returns:
            list of filenames and boolean indicating if sent
        """

        self._print_received("send_all_data", {"file_dir": self.file_dir})
        successes = []

        p = Path(self.file_dir)
        if not p.exists():
            self._debug(f"send_all_data() skipped missing dir: {p}")
            self._print_executed("send_all_data", successes)
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

        self._debug(f"send_all_data() processed {len(successes)} files")
        self._print_executed("send_all_data", successes)

        return successes

    def _build_payload_from_sample_obj(self, sample: Sample):
        self._print_received(
            "_build_payload_from_sample_obj",
            {"sample_name": getattr(sample, "name", None)},
        )
        if sample is None:
            self._print_executed("_build_payload_from_sample_obj", None)
            return None

        now_iso = datetime.now(timezone.utc).isoformat()
        data_points = []
        for idx, value in enumerate(sample.data or []):
            try:
                absorbance = float(value)
            except (TypeError, ValueError):
                continue
            wavelength = float(idx) * float(sample.interval or 1.0)
            data_points.append({"wavelength": wavelength, "absorbance": absorbance})

        payload = {
            "sampleID": sample.name,
            "owner": self.user,
            "datetime": now_iso,
            "ranges": [],
            "settings": {
                "type": getattr(sample, "type", "unknown"),
                "interval": str(getattr(sample, "interval", "")),
            },
            "data": data_points,
        }
        self._debug(
            f"_build_payload_from_sample_obj() sample={sample.name}, points={len(data_points)}"
        )
        self._print_executed(
            "_build_payload_from_sample_obj",
            {"sampleID": payload.get("sampleID"), "points": len(data_points)},
        )
        return payload

    def send_data(self, samplePath):
        """
        Converts a sample to a file and sends all the unsent data to ICN

        Args:
            samplePath (String): The path to the sample that is being sent to ICN

        Returns:
            Boolean: True if it successful send all unsent data
        """

        self._print_received("send_data", {"samplePath": str(samplePath)})
        # ensure logged in and session valid
        if not self.is_logged_in():
            self._debug("send_data() rejected: not logged in")
            self._print_executed("send_data", False)
            return False

        if isinstance(samplePath, Sample):
            parsed = self._build_payload_from_sample_obj(samplePath)
            source_desc = f"Sample(name={samplePath.name})"
        else:
            parsed = self.parse_sample(samplePath)
            source_desc = str(samplePath)

        if not parsed:
            self._debug(f"send_data() parse failed source={source_desc}")
            self._print_executed("send_data", False)
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

        self._debug(
            f"TX POST {url_input} source={source_desc}, dataKey={data_key}, points={len(data_array)}"
        )
        self._print_tx("POST", url_input, json_input)

        try:
            response = requests.post(url_input, json=json_input, timeout=15)
            payload = response.json()
            self._debug(
                f"RX status_code={response.status_code}, success={payload.get('success')}"
            )
            if payload.get("success"):
                self._print_executed("send_data", True)
                return True
        except Exception as exc:
            self._debug(f"send_data() exception: {exc}")
            self._print_executed("send_data", False)
            return False

        self._print_executed("send_data", False)
        return False

    def parse_sample(self, sampleName):
        """
        Converts a sample to a JSON object that can be sent to ICN

        Args:
            sampleName (String): The name of the sample that is being converted

        Returns:
            JSON: The JSON object that represents the sample
        """

        self._print_received("parse_sample", {"sampleName": sampleName})
        # sampleName can be absolute or relative to file_dir
        p = Path(sampleName)
        if not p.exists():
            p = Path(self.file_dir) / sampleName
        if not p.exists():
            self._debug(f"parse_sample() missing file: {sampleName}")
            self._print_executed("parse_sample", None)
            return None

        stem = p.stem
        parts = stem.rsplit("_", 2)
        if len(parts) != 3:
            self._debug(f"parse_sample() invalid filename format: {p.name}")
            self._print_executed("parse_sample", None)
            return None
        owner, dt_str, flag = parts

        # validate datetime
        try:
            _ = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except Exception:
            self._debug(f"parse_sample() invalid datetime token: {dt_str}")
            self._print_executed("parse_sample", None)
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
                    num_field = rest[26 : 26 + 4] if len(rest) >= 30 else rest[24:]
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

        parsed = {
            "sampleID": stem,
            "owner": owner,
            "datetime": dt_str,
            "ranges": ranges,
            "settings": settings,
            "data": data,
        }
        self._debug(
            f"parse_sample() parsed sampleID={stem}, ranges={len(ranges)}, data_points={len(data)}"
        )
        self._print_executed(
            "parse_sample",
            {"sampleID": stem, "ranges": len(ranges), "data_points": len(data)},
        )
        return parsed
