import logging
import socket
import types

__all__ = ["CBPComponent"]


class CBPComponent:
    """This class is for implementing the CBP component.

    The component implements a python wrapper over :term:`DMC` code written by DFM Manufacturing.
    The following api exposes commands that move the motors of the CBP, sets the focus and selects the mask.

    Parameters
    ----------
    address : `str`
       The ip address of the CBP galil controller.
    port : `int`
        The port to connect to the CBP galil controller.

    Attributes
    ----------
    log : `logging.Logger`
        The logger for the component

    socket : `socket.Socket`
        The socket that handles the TCP/IP connection for the CBP

    altitude : `float`
        The value of the CBP altitude encoder in degress.

    azimuth : `float`
        The value of the CBP azimuth encoder in degrees.

    mask : `str`
        The current mask as named in the mask_dictionary

    mask_rotation : `float`
        The current value of the mask rotation encoder in degrees.

    masks : `SimpleNamespace`
        A simplenamespace that contains the mask names and rotation values along with the id.

    focus : `float`
        The current value of the focus encoder in microns.

    panic_status : `float`
        The current value of the panic variable in the CBP dmc code.
        A non-zero value represents a panic state and causes the motors to cease functioning until panic is
        dealt with or goes away.
        This status is related to the other statuses.

    auto_park : `float`
        The current value of the auto_park variable.
        If this value is one, that means that CBP suffered a power loss that lasted more than 12 seconds and
        was on battery back up.
        The CBP will then park itself automatically, moving azimuth to 0 and altitude to -70 and lock focus
        and mask.
        To unpark CBP, the park variable should be set to zero.

    park : `float`
        The current value of the park variable.
        This value can be set to one or zero, if set to one it will park the CBP if set to zero it will
        unpark.

    azimuth_status : `float`
        This is the current value of the status of the azimuth encoder.
        If this value is non-zero, the encoder has an error.

    altitude_status : `float`
        This is the current value of the status of the altitude encoder.
        If this value is non-zero, the encoder has an error.

    mask_select_status : `float`
        This is the current value of the status of the mask selection encoder.
        If this value is non-zero, the encoder has an error.

    mask_rotate_status : `float`
        This is the current value of the status of the mask rotation encoder.
        If this value is non-zero, the encoder has an error.

    focus_status : `float`
        This is the current value of the status of the focus encoder.
        If this value is non-zero, the encoder has an error.

    Notes
    -----

    The class uses the python socket module to build TCP/IP connections to the galil controller mounted onto
    CBP.
    The underlying api is built on :term:`DMC`.
    """

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.socket = None
        self.altitude = None
        self.azimuth = None
        self.mask = None
        self.mask_rotation = None
        self.masks = types.SimpleNamespace(
            mask1=types.SimpleNamespace(name="Not a mask 1", rotation=0, id=1.0),
            mask2=types.SimpleNamespace(name="Not a mask 2", rotation=0, id=2.0),
            mask3=types.SimpleNamespace(name="Not a mask 3", rotation=0, id=3.0),
            mask4=types.SimpleNamespace(name="Not a mask 4", rotation=0, id=4.0),
            mask5=types.SimpleNamespace(name="Not a mask 5", rotation=0, id=5.0),
            mask9=types.SimpleNamespace(name="Unknown Mask", rotation=0, id=9.0),
        )
        self.mask_dictionary = {
            self.masks.mask1.name: self.masks.mask1,
            self.masks.mask2.name: self.masks.mask2,
            self.masks.mask3.name: self.masks.mask3,
            self.masks.mask4.name: self.masks.mask4,
            self.masks.mask5.name: self.masks.mask5,
            self.masks.mask9.name: self.masks.mask9,
        }
        self.mask_id_dictionary = {
            self.masks.mask1.id: self.masks.mask1,
            self.masks.mask2.id: self.masks.mask2,
            self.masks.mask3.id: self.masks.mask3,
            self.masks.mask4.id: self.masks.mask4,
            self.masks.mask5.id: self.masks.mask5,
            self.masks.mask9.id: self.masks.mask9,
        }
        self.focus = None
        self._address = None
        self._port = None
        self.panic_status = None
        self.auto_park = None
        self.park = None
        self.azimuth_status = None
        self.altitude_status = None
        self.mask_select_status = None
        self.mask_rotate_status = None
        self.focus_status = None
        self.simulation_mode = 0
        self.log.info("CBP component initialized")

    def parse_reply(self):
        """Parses the reply to remove the carriage return and new line.

        Returns
        -------
        str
            The reply that was parsed.

        """
        if self.simulation_mode == 0:
            parsed_reply = self.socket.recv(128).decode("ascii").split("\r")[0]
        elif self.simulation_mode == 1:
            parsed_reply = "0"
        return parsed_reply

    def connect(self):
        """Creates a socket and connects to the CBP's static address and designated port.


        Returns
        -------
        None
            Nothing

        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self._address, self._port))
            self.log.debug(
                "CBP connected to {0} on port {1}".format(self._address, self._port)
            )
        except TimeoutError as te:
            self.log.error("Socket timed out")
            raise te

    def disconnect(self):
        self.socket.close()
        self.socket = None

    def get_azimuth(self):
        """Gets azimuth value from azimuth encoder which is in degrees.

        Returns
        -------

        """
        self.socket.sendall("az=?\r".encode("ascii"))
        self.azimuth = float(self.parse_reply())

    def move_azimuth(self, position: float):
        """This moves the horizontal axis to the value sent by the user.

        Parameters
        ----------
        position: float
            This is the value in degrees that is sent to the CBP in order to move the horizontal axis.

        Returns
        -------
        None

        """
        if position < -45 or position > 45:
            raise ValueError("New azimuth value exceeds Azimuth limit.")
        else:
            self.socket.sendall("new_az={0:f}\r".format(position).encode("ascii"))
            reply = self.socket.recv(128).decode("ascii", "ignore")
            self.log.debug(reply)

    def get_altitude(self):
        """This gets the altitude value from the altitude encoder in degrees.

        Returns
        -------
        None

        """
        self.log.debug("get_altitude sent")
        self.socket.sendall("alt=?\r".encode("ascii"))
        self.altitude = float(self.parse_reply())

    def move_altitude(self, position: float):
        """This moves the vertical axis to the value that the user sent.

        Parameters
        ----------
        position: float
            The value to move the altitude to which is in degrees.

        Returns
        -------
        None

        """
        if position < -69 or position > 45:
            raise ValueError("New altitude value exceeds altitude limit.")
        else:
            self.socket.sendall("new_alt={0:f}\r".format(position).encode("ascii"))
            reply = self.socket.recv(128).decode("ascii", "ignore")
            self.log.debug(reply)

    def get_focus(self):
        """This gets the value of the focus encoder. Units: microns

        Returns
        -------
        None

        """
        self.socket.sendall("foc=?\r".encode("ascii"))
        self.focus = float(self.parse_reply())

    def change_focus(self, position: int):
        """This changes the focus to whatever value the user sent.

        Parameters
        ----------
        position: int
            The value of the new focus in microns.

        Returns
        -------
        None

        """
        if position < 0 or position > 13000:
            raise ValueError("New focus value exceeds focus limit.")
        else:
            self.socket.sendall("new_foc={0:f}\r".format(position).encode("ascii"))
            reply = self.socket.recv(128).decode("ascii", "ignore")
            self.log.debug(reply)

    def get_mask(self):
        """This gets the current mask value from the encoder which is converted into the name of the mask.

        Returns
        -------
        None

        """
        self.socket.sendall("msk=?\r".encode("ascii"))
        self.mask = self.mask_id_dictionary[float(self.parse_reply())].name

    def set_mask(self, mask: str):
        """This sets the mask value

        Parameters
        ----------
        mask: str
            This is the name of the mask which is converted to an int using a dictionary.

        Returns
        -------
        None

        """
        if mask not in self.mask_dictionary:
            raise KeyError(
                "Mask is not in dictionary, name may need to added or changed."
            )
        self.socket.sendall(
            "new_msk={0:f}\r".format(self.mask_dictionary[mask].id).encode("ascii")
        )
        reply = self.socket.recv(128).decode("ascii", "ignore")
        self.log.debug(reply)

    def get_mask_rotation(self):
        """This gets the mask rotation value from the encoder which is in degrees.

        Returns
        -------
        None

        """
        self.socket.sendall("rot=?\r".encode("ascii"))
        self.mask_rotation = float(self.parse_reply())

    def set_mask_rotation(self, mask_rotation: float):
        """This sets the mask rotation

        Parameters
        ----------
        mask_rotation: float
            The mask_rotation value that will be sent.

        Returns
        -------
        None

        """
        if mask_rotation < 0 or mask_rotation > 360:
            raise ValueError("New mask rotation value exceeds mask rotation limits.")
        self.socket.sendall("new_rot={0:f}\r".format(mask_rotation).encode("ascii"))
        reply = self.socket.recv(128).decode("ascii", "ignore")
        self.log.debug(reply)

    def check_panic_status(self):
        """Gets the panic variable from CBP

        Returns
        -------
        None

        """
        self.socket.sendall("wdpanic=?\r".encode("ascii"))
        self.panic_status = float(self.parse_reply())

    def check_auto_park(self):
        """Gets the autopark variable from CBP

        Returns
        -------
        None

        """
        self.socket.sendall("autopark=?\r".encode("ascii"))
        self.auto_park = float(self.parse_reply())

    def check_park(self):
        """Gets the park variable from CBP

        Returns
        -------
        None

        """
        self.socket.sendall("park=?\r".encode("ascii"))
        self.park = float(self.parse_reply())

    def set_park(self, park: int = 0):
        """A function that tells the CBP to park or unpark depending on the value given.

        Parameters
        ----------
        park: int {0,1}
            A boolean int which tells the CBP to park or not.

        Returns
        -------
        None

        """
        if park not in [0, 1]:
            raise ValueError("park must be binary value that is either 1 or 0.")
        self.socket.sendall("park={0:f}\r".format(park).encode("ascii"))
        reply = self.socket.recv(128).decode("ascii", "ignore")
        self.log.debug(reply)

    def check_cbp_status(self):
        """Checks the status of the encoders.

        Returns
        -------
        None

        """
        self.socket.sendall("AAstat=?\r".encode("ascii"))
        self.azimuth_status = float(self.parse_reply())
        self.socket.sendall("ABstat=?\r".encode("ascii"))
        self.altitude_status = float(self.parse_reply())
        self.socket.sendall("ACstat=?\r".encode("ascii"))
        self.mask_select_status = float(self.parse_reply())
        self.socket.sendall("ADstat=?\r".encode("ascii"))
        self.mask_rotate_status = float(self.parse_reply())
        self.socket.sendall("AEstat=?\r".encode("ascii"))
        self.focus_status = float(self.parse_reply())

    def get_cbp_telemetry(self):
        """Gets the position data of the CBP.

        Returns
        -------
        None

        """
        self.get_altitude()
        self.get_azimuth()
        self.get_focus()
        self.get_mask()
        self.get_mask_rotation()

    def configure(self, config):
        self.config = config
        self._address = self.config.address
        self._port = self.config.port
        self.masks.mask1.name = self.config.mask1.name
        self.masks.mask1.rotation = self.config.mask1.rotation
        self.masks.mask2.name = self.config.mask2.name
        self.masks.mask2.rotation = self.config.mask2.rotation
        self.masks.mask3.name = self.config.mask3.name
        self.masks.mask3.rotation = self.config.mask3.rotation
        self.masks.mask4.name = self.config.mask4.name
        self.masks.mask4.rotation = self.config.mask4.rotation
        self.masks.mask5.name = self.config.mask5.name
        self.masks.mask5.rotation = self.config.mask5.rotation

    def publish(self):
        """This updates the attributes within the component.

        Returns
        -------
        None

        """
        self.check_panic_status()
        self.check_cbp_status()
        self.check_park()
        self.check_auto_park()
        self.get_cbp_telemetry()

    def set_simulation_mode(self, simulation_mode):
        self.simulation_mode = simulation_mode
