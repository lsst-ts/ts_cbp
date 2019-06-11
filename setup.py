from setuptools import setup
setup_reqs=['setuptools_scm']
install_reqs=['argh']
test_reqs=['pytest','pytest-flake8']
setup(
    name="ts_cbp",
    use_scm_version = True,
    setup_requires=setup_reqs,
    install_requires=install_reqs,
    entry_points={
        'console_scripts': ['cbp_csc=lsst.ts.cbp.cli:main']
    },
    extras_require={'dev':setup_reqs+install_reqs+test_reqs+['documenteer[pipelines]','sphinx-argparse']},
    packages=['lsst.ts.cbp'],
)
