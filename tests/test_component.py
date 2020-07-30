from lsst.ts.cbp.component import CBPComponent
import pytest
import subprocess
import time


def setup_module(module):
    module.simulator_process = subprocess.Popen(["lewis", "-k", "lsst.ts.cbp", "simulator"])


def teardown_module(module):
    module.simulator_process.terminate()


class TestCbpComponent:

    @pytest.fixture(scope="module")
    def cbp(self):
        cbp = CBPComponent()
        cbp._address = "localhost"
        cbp._port = 9999
        time.sleep(7)
        cbp.connect()
        return cbp

    def test_parse_reply(self, cbp, mocker):
        mocker.patch.object(cbp, 'socket')
        mocker.patch.object(cbp.socket, 'recv', return_value=b"5.5\r")
        reply = cbp.parse_reply()
        assert reply == "5.5"

    @pytest.mark.parametrize(
        "mask_float, expected_name",
        [
            ("1.0", "Not a mask 1"),
            ("2.0", "Not a mask 2"),
            ("3.0", "Not a mask 3"),
            ("4.0", "Not a mask 4"),
            ("5.0", "Not a mask 5"),
            ("9.0", "Unknown Mask")])
    def test_get_mask(self, cbp, mask_float, expected_name):
        cbp.set_mask(expected_name)
        cbp.get_mask()
        assert cbp.mask == expected_name

    @pytest.mark.parametrize(
        "mask_name,mask_float",
        [
            ("Not a mask 1", b"new_msk=1.000000"),
            ("Not a mask 2", b"new_msk=2.000000"),
            ("Not a mask 3", b"new_msk=3.000000"),
            ("Not a mask 4", b"new_msk=4.000000"),
            ("Not a mask 5", b"new_msk=5.000000"),
            ("Unknown Mask", b"new_msk=9.000000")])
    def test_set_mask(self, cbp, mask_name, mask_float):
        cbp.set_mask(mask_name)
        assert "new_msk={0:f}".format(cbp.mask_dictionary[mask_name].id).encode('ascii') == mask_float

    @pytest.mark.parametrize("alt", [(-70), (46), (0)])
    def test_move_altitude(self, cbp, alt):
        if alt not in range(-69, 46):
            with pytest.raises(ValueError):
                cbp.move_altitude(alt)
        else:
            cbp.move_altitude(alt)

    @pytest.mark.parametrize("az", [(-46), (46), (0)])
    def test_move_azimuth(self, cbp, az):
        if az not in range(-45, 46):
            with pytest.raises(ValueError):
                cbp.move_azimuth(az)
        else:
            cbp.move_azimuth(az)

    @pytest.mark.parametrize("foc", [(-1), (13001), (24)])
    def test_change_focus(self, cbp, foc):
        if foc not in range(0, 13001):
            with pytest.raises(ValueError):
                cbp.change_focus(foc)
        else:
            cbp.change_focus(foc)

    @pytest.mark.parametrize("msk_rot", [(-1), (361), (30)])
    def test_set_mask_rotation(self, cbp, msk_rot):
        if msk_rot not in range(0, 361):
            with pytest.raises(ValueError):
                cbp.set_mask_rotation(msk_rot)
        else:
            cbp.set_mask_rotation(msk_rot)
