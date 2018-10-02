import socket
from time import sleep


class CBPComponent:
    """
    This class is for implementing the CBP component

    Parameters
    ----------

    address : str
    port : int
    """
    def __init__(self,address: str, port: int):
        self.socket = None
        self.altitude = None
        self.azimuth = None
        self.mask = None
        self.mask_rotation = None
        self.mask_dictionary = {}
        self.focus = None
        self._address = address
        self._port = port
        self.get_cbp_telemetry()
        self.panic_status = None
        self.check_panic_status()
        self.azimuth_status = None
        self.altitude_status = None
        self.mask_select_status = None
        self.mask_rotate_status = None
        self.focus_status = None
        self.check_cbp_status()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.socket.connect((self._address, self._port))

    def get_azimuth(self):
        self.connect()
        sleep(1)
        self.socket.sendall("az=?\r".encode('ascii'))
        self.azimuth = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.close()

    def move_azimuth(self,position: float):
        self.connect()
        self.socket.sendall("new_az={0:f}\r".format(position).encode('ascii'))
        reply = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.close()
        sleep(4.5)
        self.publish()


    def get_altitude(self):
        self.connect()
        self.socket.sendall("alt=?\r".encode('ascii'))
        self.altitude = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.close()

    def move_altitude(self,position: float):
        raise NotImplementedError
        self.connect()
        self.socket.sendall("new_alt{0:f}\r".format(position).encode('ascii'))
        reply = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.close()
        sleep(4.5)
        self.publish()

    def get_focus(self):
        self.connect()
        self.socket.sendall("foc=?\r".encode('ascii'))
        self.focus = self.socket.recv(128).decode('ascii')
        self.socket.close()

    def change_focus(self,position: int):
        self.connect()
        self.socket.sendall("new_foc={0:f}\r".format(position).encode('ascii'))
        reply = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.close()
        sleep(4.5)
        self.publish()

    def get_mask(self):
        self.connect()
        self.socket.sendall("msk=?\r".encode('ascii'))
        self.mask = self.socket.recv(128).decode('ascii')
        self.socket.close()

    def set_mask(self, mask: str):
        raise NotImplementedError
        self.connect()
        self.socket.sendall("new_msk={0:f}".format(mask['id']).encode('ascii'))
        reply = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.close()
        sleep(4.5)
        self.publish()

    def get_mask_rotation(self):
        self.connect()
        self.socket.sendall("rot=?\r".encode('ascii'))
        self.mask_rotation = self.socket.recv(128).decode('ascii')
        self.socket.close()

    def set_mask_rotation(self,mask_rotation: float):
        self.connect()
        self.socket.sendall("new_rot={0:f}".format(mask_rotation).encode('ascii'))
        reply = self.socket.recv(128).decode('ascii', 'ignore')
        sleep(4.5)
        self.socket.close()

    def check_panic_status(self):
        self.connect()
        self.socket.sendall("wdpanic=?\r".encode('ascii'))
        self.panic_status = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.close()

    def check_cbp_status(self):
        self.connect()
        self.socket.sendall("AAstat=?\r".encode('ascii'))
        self.azimuth_status = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.close()
        self.connect()
        self.socket.sendall("ABstat=?\r".encode('ascii'))
        self.altitude_status = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.close()
        self.connect()
        self.socket.sendall("ACstat=?\r".encode('ascii'))
        self.mask_select_status = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.close()
        self.connect()
        self.socket.sendall("ADstat=?\r".encode('ascii'))
        self.mask_rotate_status = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.close()
        self.connect()
        self.socket.sendall("AEstat=?\r".encode('ascii'))
        self.focus_status = self.socket.recv(128).decode('ascii', 'ignore')
        self.socket.close()

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
    cbp.move_azimuth(0)
    print("moved")


if __name__ == '__main__':
    main()
