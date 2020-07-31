from documenteer.sphinxconfig.stackconf import build_package_configs
from pkg_resources import get_distribution
_g = globals()
_g.update(build_package_configs(
    project_name='ts-CBP',
    version=get_distribution('ts-cbp').version
    ))
extensions.append('releases')
extensions.append('sphinxarg.ext')
extensions.append('sphinx-jsonschema')
