from setuptools import setup

setup(
    name="ts_cbp",
    use_scm_version = True,
    setup_requires=['setuptools_scm'],
    install_requires=['pytest==3.2.1','sphinx==1.8.1','argh==0.26.2'],
    dependency_links = ["git+git://github.com/lsst-ts/salobj.git@3.3.0#egg=salobj-3.3.0"],
    entry_points={
        'console_scripts': ['cbp_csc=lsst.ts.cbp.cli:main']
    },
    packages=['lsst.ts.cbp'],
)
