from setuptools import setup

setup(
    name="ts_cbp",
    use_scm_version = True,
    setup_requires=['setuptools_scm'],
    install_requires=['pytest==3.2.1'],
    dependency_links = ["git+git://github.com/lsst-ts/salobj.git@2.3.0#egg=salobj-2.3.0"],
    packages=['lsst.ts.cbp']
)