import logging
import socket


class CBPComponent:
    """
    This class is for implementing the CBP component

    Parameters
    ----------

    address : str
    port : int
    """
    def __init__(self,address: str, port: int):
        self.log = logging.getLogger(__name__)
        self.socket = None
        self.altitude = None
        self.azimuth = None
        self.mask = None
        self.mask_rotation = None
        self.mask_dictionary = {}
        self.focus = None
        self._address = address
        self._port = port
        self.connect()
        self.get_cbp_telemetry()
        self.panic_status = None
        self.check_panic_status()
        self.azimuth_status = None
        self.altitude_status = None
        self.mask_select_status = None
        self.mask_rotate_status = None
        self.focus_status = None
        self.check_cbp_status()
        self.log.info("CBP initialized")

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.socket.connect((self._address, self._port))
        self.log.debug("CBP connected to {0} on port {1}".format(self._address, self._port))

    def get_azimuth(self):
        self.socket.sendall("az=?\r".encode('ascii'))
        self.azimuth = float(self.socket.recv(128).decode('ascii', 'ignore').split("\r")[0])

    def move_azimuth(self,position: float):
        self.socket.sendall("new_az={0:f}\r".format(position).encode('ascii'))
        reply = self.socket.recv(128).decode('ascii', 'ignore')


    def get_altitude(self):
        self.log.debug("get_altitude sent")
        self.socket.sendall("alt=?\r".encode('ascii'))
        self.altitude = float(self.socket.recv(128).decode('ascii', 'ignore').split("\r")[0])

    def move_altitude(self,position: float):
        self.socket.sendall("new_alt={0:f}\r".format(position).encode('ascii'))
        reply = self.socket.recv(128).decode('ascii', 'ignore')

    def get_focus(self):
        self.socket.sendall("foc=?\r".encode('ascii'))
        self.focus = self.socket.recv(128).decode('ascii').split("\r")[0]

    def change_focus(self,position: int):
        self.socket.sendall("new_foc={0:f}\r".format(position).encode('ascii'))
        reply = self.socket.recv(128).decode('ascii', 'ignore')

    def get_mask(self):
        self.socket.sendall("msk=?\r".encode('ascii'))
        self.mask = self.socket.recv(128).decode('ascii').split("\r")[0]

    def set_mask(self, mask: str):
        self.socket.sendall("new_msk={0:f}".format(self.mask_dictionary[mask]).encode('ascii'))
        reply = self.socket.recv(128).decode('ascii', 'ignore')

    def get_mask_rotation(self):
        self.socket.sendall("rot=?\r".encode('ascii'))
        self.mask_rotation = float(self.socket.recv(128).decode('ascii').split("\r")[0])

    def set_mask_rotation(self,mask_rotation: float):
        self.socket.sendall("new_rot={0:f}".format(mask_rotation).encode('ascii'))
        reply = self.socket.recv(128).decode('ascii', 'ignore')

    def check_panic_status(self):
        self.socket.sendall("wdpanic=?\r".encode('ascii'))
        self.panic_status = float(self.socket.recv(128).decode('ascii', 'ignore').split('\r')[0])

    def check_cbp_status(self):
        self.socket.sendall("AAstat=?\r".encode('ascii'))
        self.azimuth_status = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.sendall("ABstat=?\r".encode('ascii'))
        self.altitude_status = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.sendall("ACstat=?\r".encode('ascii'))
        self.mask_select_status = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.sendall("ADstat=?\r".encode('ascii'))
        self.mask_rotate_status = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.sendall("AEstat=?\r".encode('ascii'))
        self.focus_status = self.socket.recv(128).decode('ascii', 'ignore')

    def get_cbp_telemetry(self):
        self.get_altitude()
        self.get_azimuth()
        self.get_focus()
        self.get_mask()
        self.get_mask_rotation()

    def publish(self):
        self.check_panic_status()
        self.check_cbp_status()
        self.get_cbp_telemetry()


def main():
    cbp = CBPComponent("140.252.33.12", 5000)
    print("")


if __name__ == '__main__':
    main()
