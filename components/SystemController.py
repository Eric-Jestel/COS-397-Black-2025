# This is the system controller

from pathlib import Path
from datetime import datetime

try:
    from InstrumentController import InstrumentController
    from ServerController import ServerController
except ImportError:
    from components.InstrumentController import InstrumentController
    from components.ServerController import ServerController

print("SystemController imported")


# still checking linting
# ------------------------------------------------------------------------------------------------------------------------------------------
class SystemController:

    # I need variables

    # ------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(
        self, PROJECT_ROOT,
        server_controller_cls=ServerController,
        instrument_controller_cls=InstrumentController,
        file_dir=None,
        debug: bool = True,
    ):
        # used for logging to communicate system processes
        print(
            "[SystemController][RECEIVED] __init__ "
            f"server_controller_cls={server_controller_cls.__name__}, "
            f"instrument_controller_cls={instrument_controller_cls.__name__}, "
            f"file_dir={file_dir}, debug={debug}"
        )
        self.PROJECT_ROOT = PROJECT_ROOT
        self.debug = bool(debug)
        sample_dir = file_dir or str(Path(__file__).parent / "sample_data")
        self.ServController = server_controller_cls(
            self.PROJECT_ROOT, file_dir=sample_dir, debug=self.debug
        )
        self.InstController = instrument_controller_cls(PROJECT_ROOT=self.PROJECT_ROOT, debug=self.debug)
        # needed a dictionary for error codes
        self.ErrorDictionary = {
            0: "Good to go",
            100: "Machine is not connecting",
            110: "Server is not connecting",
            220: "Not a valid Account",
            330: "User not logged in",
            300: "No active session",
            400: "No data",
            550: "No blank to set",
        }
        print("[SystemController][EXECUTED] __init__ controllers initialized")

    # this function verifies a function was called
    def _print_received(self, command: str, payload=None) -> None:
        print(f"[SystemController][RECEIVED] {command} payload={payload}")

    # this function verifies a function was executed
    def _print_executed(self, command: str, result=None) -> None:
        print(f"[SystemController][EXECUTED] {command} result={result}")

    # sends a debug message informing individuals of the status of a given function
    def _debug(self, message: str) -> None:
        if self.debug:
            print(f"[SystemController] {message}")

    def _instrument_ready(self) -> bool:
        # logs _instrument_ready function was called
        self._print_received("_instrument_ready")
        # attempts to get a 'ping' function from the Instrument Controller
        ping = getattr(self.InstController, "ping", None)
        # checks to see if the Instrument Controller connected has a 'ping' function
        if callable(ping):
            ready = bool(ping())
            self._debug(f"_instrument_ready() via ping -> {ready}")
            # logs functionality of ping
            self._print_executed("_instrument_ready", ready)
            return ready
        ready = bool(self.InstController)
        self._debug(f"_instrument_ready() fallback -> {ready}")
        # logs status of the Instrument Controller to see if it is connected
        self._print_executed("_instrument_ready", ready)
        return ready

    def _server_ready(self) -> bool:
        # logs _server_ready function was called
        self._print_received("_server_ready")
        # attempts to get a 'connect' function from the Server Controller
        connect = getattr(self.ServController, "connect", None)
        # verifies the Server Controller has a 'connect' function
        if callable(connect):
            ready = bool(connect())
            self._debug(f"_server_ready() via connect -> {ready}")
            # logs that the function was executed
            self._print_executed("_server_ready", ready)
            return ready
        try:
            # sees if the Server Controller is able to ping
            ready = bool(self.ServController.ping())
            self._debug(f"_server_ready() via ping -> {ready}")
            # logs functionality of the ping function
            self._print_executed("_server_ready", ready)
            return ready
        except Exception as exc:
            self._debug(f"_server_ready() ping exception: {exc}")
            # logs nonfunctionality of the ping function
            self._print_executed("_server_ready", False)
            return False

    # ------------------------------------------------------------------------------------------------------------------------------------------
    def startUp(self):
        # logs startUpfunction was called
        self._print_received("startUp")
        self._debug("startUp() starting")
        self._print_received("InstrumentController.setup")
        # attempts Instrument Controller setup procedures
        InstConn = self.InstController.setup()
        # logs setup function was executed
        self._print_executed("InstrumentController.setup", InstConn)
        self._debug(f"startUp() instrument setup -> {InstConn}")
        # verify machine successfully starts up
        if InstConn:
            ServConn = self._server_ready()
            self._debug(f"startUp() server connect -> {ServConn}")
            # verify server is ready
            if ServConn:
                # logs startUp worked
                self._print_executed("startUp", 0)
                return 000
            else:
                # logs Server Controller didnt successfully startup
                self._print_executed("startUp", 110)
                return 110
        else:
            # logs Instrument Controller didn't successfully startup
            self._print_executed("startUp", 100)
            return 100

    # ------------------------------------------------------------------------------------------------------------------------------------------
    def signIn(self, username):
        # logs signIn was called
        self._print_received("signIn", {"username": username})
        self._debug(f"signIn() username={username}")
        # verify connection to ICN through ping
        if self.ServController.ping():
            # logs attempt to login user
            self._print_received("ServerController.login", {"username": username})
            # send information to server controller to sign in
            loggedIn = self.ServController.login(username)
            # logs status of attempt to login user was executed
            self._print_executed("ServerController.login", loggedIn)
            self._debug(f"signIn() login response={loggedIn}")
            # verifies user is logged in
            if loggedIn:
                # logs signIn worked
                self._print_executed("signIn", 0)
                return 000
            else:
                # logs signIn failed to sign user in but server is connected
                # this suggests the username is incorrect
                self._print_executed("signIn", 220)
                return 220
        else:
            # logs the Server Controller isn't pinging... uh oh
            self._print_executed("signIn", 110)
            return 110

    # ------------------------------------------------------------------------------------------------------------------------------------------
    def signOut(self):
        # logs signOut was called
        self._print_received("signOut")
        self._debug("signOut() invoked")
        # verify server connectivity
        if self.ServController.ping():
            # logs and sends all data to the server controller after taking samples
            self._print_received("ServerController.send_all_data")
            upload_result = self.ServController.send_all_data()
            # logs execution of sending all data
            self._print_executed("ServerController.send_all_data", upload_result)
            self._debug(f"signOut() send_all_data -> {upload_result}")
            # check to see if anyone is logged in
            if self.ServController.is_logged_in():
                self._print_received("ServerController.logout")
                # logs them out
                if self.ServController.logout():
                    # logs logout was executed successfully
                    self._print_executed("ServerController.logout", True)
                    # logs signOut was executed successfully
                    self._print_executed("signOut", 0)
                    return 000
                else:
                    # logs logout was executed unsuccessfully
                    self._print_executed("ServerController.logout", False)
                    # logs signOut was unable to successfully execute
                    self._print_executed("signOut", 330)
                    return 330
            else:
                # logs no user is logged in meaning there is no active session
                self._print_executed("signOut", 300)
                return 300
        else:
            # logs the server didn't successfully ping
            self._print_executed("signOut", 110)
            return 110

    # ------------------------------------------------------------------------------------------------------------------------------------------
    def runLabMachine(self):
        # logs that the function was called
        self._print_received("runLabMachine")
        self._debug("runLabMachine() invoked")
        # verify instrument connection
        if self.InstController.ping():
            # logs and sends instructions to machine to run test
            self._print_received("InstrumentController.take_sample")
            targetFilename = datetime.now().strftime("%Y%m%d_%H%M%SZ") + ".csv"
            csv_path = self.InstController.take_sample(targetFilename)
            # logs execution of sending data with the status of data
            self._print_executed("InstrumentController.take_sample", csv_path)
            self._debug(f"runLabMachine() sample received={bool(csv_path)}")
            # checks if data exists
            if csv_path:
                self.ServController.process_sample(csv_path)
                # verify server connection
                if self._server_ready():
                    # sends data to UI somehow and send data to server controller to send to the ICN
                    self._print_received("ServerController.send_all_data")
                    sent = self.ServController.send_all_data()
                    self._print_executed("ServerController.send_all_data", sent)
                    self._debug(f"runLabMachine() send_all_data -> {sent}")
                    for fileSent in sent:
                        if fileSent[1] is False:
                            self._debug(f"runLabMachine() failed to send {fileSent[0]}")
                        if fileSent[0] == csv_path:
                            self._print_executed("runLabMachine", (0, csv_path))
                            return 000, csv_path
                    self._print_received("ServerController.send_data", csv_path)
                    sent = self.ServController.send_data(csv_path)
                    # logs functionality of sending data
                    self._print_executed("ServerController.send_data", sent)
                    self._debug(f"runLabMachine() send_data -> {sent}")
                    # verifies the data was sent successfully
                    if sent:
                        # logs data successfully being sent
                        self._print_executed("runLabMachine", (0, csv_path))
                        return 000, csv_path
                    # logs data unsuccessfully being sent
                    self._print_executed("runLabMachine", (110, None))
                    return 110, None
                else:
                    # logs server unable to ping
                    self._print_executed("runLabMachine", (110, None))
                    return 110, None
            else:
                # logs lack of data :(
                self._print_executed("runLabMachine", (400, None))
                return 400, None
        else:
            # logs machine unable to ping
            self._print_executed("runLabMachine", (100, None))
            return 100, None

    # ------------------------------------------------------------------------------------------------------------------------------------------
    def takeBlank(self, filename=None):
        # logs takeBlank was called
        self._print_received("takeBlank", {"filename": filename})
        self._debug(f"takeBlank() filename={filename}")
        # verify instrument connection
        if self.InstController.ping():
            # checks if there is a file
            if filename is None:
                # makes a filename for the blank to be stored
                filename = str(
                    Path(self.ServController.file_dir)
                    / f"blank_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                )
            # logs filename path
            self._print_received(
                "InstrumentController.take_blank", {"filename": filename}
            )
            # sends instructions to machine to run test
            data = self.InstController.take_blank(filename)
            self._print_executed("InstrumentController.take_blank", data)
            self._debug(f"takeBlank() result={data}")
            # checks to see if the data exists
            if data:
                # sets as blank file
                self._print_executed("takeBlank", (0, self.InstController.blank_file))
                return 000, self.InstController.blank_file
            else:
                # logs no data is present
                self._print_executed("takeBlank", (400, None))
                return 400, None
        else:
            # logs Instrument Controller couldn't ping
            self._print_executed("takeBlank", (100, None))
            return 100, None

    # ------------------------------------------------------------------------------------------------------------------------------------------
    def setBlank(self, data):
        # logs setBlank was called
        self._print_received("setBlank", {"data": data})
        self._debug(f"setBlank() data={data}")
        # verify instrument connection
        if self.InstController.ping():
            # verifies there is data
            if data:
                # send instructions to machine to set data
                self._print_received("InstrumentController.set_blank", {"data": data})
                set_ok = self.InstController.set_blank(data)
                # logs data being sent
                self._print_executed("InstrumentController.set_blank", set_ok)
                self._debug(f"setBlank() set_blank -> {set_ok}")
                # checks to see if the data was set
                if set_ok:
                    # logs data was able to be set
                    self._print_executed("setBlank", 0)
                    return 000
                else:
                    # logs data was unable to be set
                    self._print_executed("setBlank", 550)
                    return 550
            else:
                # logs lack of data
                self._print_executed("setBlank", 400)
                return 400
        else:
            # logs lack of successful Instrument Controller ping
            self._print_executed("setBlank", 100)
            return 100

    # ------------------------------------------------------------------------------------------------------------------------------------------
    def takeSample(self):
        # logs takeSample was called
        self._print_received("takeSample")
        self._debug("takeSample() invoked")
        # verify instrument connection
        if self._instrument_ready():
            # logs and sends instructions to machine to run test
            self._print_received("InstrumentController.take_sample")
            data = self.InstController.take_sample()
            # logs that the function was executed
            self._print_executed("InstrumentController.take_sample", data)
            self._debug(f"takeSample() sample received={bool(data)}")
            # checks to see if data exists
            if data:
                # logs that there is data and function executed successfully
                self._print_executed("takeSample", (0, data))
                return 000, data
            else:
                # logs lock of data
                self._print_executed("takeSample", (400, None))
                return 400, None
        else:
            # logs lac of successful Instrument Controller ping
            self._print_executed("takeSample", (100, None))
            return 100, None

    # ------------------------------------------------------------------------------------------------------------------------------------------
    def stopProgram(self):
        # logs stopProgram was called
        self._print_received("stopProgram")
        self._debug("stopProgram() invoked")
        # verifies Server Controller successfully pings
        if self.ServController.ping():
            # verifies there is an active session
            if self.ServController.is_logged_in():
                # logs sends instructions for the Server controller to disconnect
                self._print_received("ServerController.logout")
                self.ServController.logout()
                # logs that the function was executed
                self._print_executed("ServerController.logout", True)
            # verify instrument connection
            if self.InstController.ping():
                # sends instructions for the Instrument Controller to shut down the machine
                self._print_received("InstrumentController.shutdown")
                shut_ok = self.InstController.shutdown()
                # logs shutdown status
                self._print_executed("InstrumentController.shutdown", shut_ok)
                self._debug(f"stopProgram() shutdown -> {shut_ok}")
                result = 000 if shut_ok else 100
                # logs status of result and returns it
                self._print_executed("stopProgram", result)
                return result
            else:
                # logs Instrument Controller is unable to ping
                self._print_executed("stopProgram", 100)
                return 100
        else:
            # logs Server Controller unable to ping
            self._print_executed("stopProgram", 110)
            return 110


# ------------------------------------------------------------------------------------------------------------------------------------------
# error code stuffs
"""
All of this is subject to change
Preabmle = 000 means that it is good to go
1) 100 = Machine is not connecting
2) 110 = Server is not connecting
3) 220 = Not a valid Account
4) 330 = User not logged in
5) 400 = No data :(
6) 550 = No blank to set
"""
# Info needed
"""
I need a way to verify server connectivity (ping it)
I need a way to verify machine connectivity (maybe ping it?)
When running the machine is there really no possible way to send
information to and from the instrument controller to the machine controller?
"""


class SystemControllerSample:

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
        self.samples.append(newSample)
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
