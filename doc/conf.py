"""Sphinx configuration file for TSSW package"""

from documenteer.sphinxconfig.stackconf import build_package_configs
import lsst.ts.cbp


_g = globals()
_g.update(
    build_package_configs(
        project_name="ts_CBP", version=lsst.ts.cbp.version.__version__
    )
)

intersphinx_mapping["ts_xml"] = ("https://ts-xml.lsst.io", None)
intersphinx_mapping["ts_salobj"] = ("https://ts-salobj.lsst.io", None)
