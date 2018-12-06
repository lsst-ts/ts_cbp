# TS_CBP

## Installation


The following assumes that 

* Centos 7 is the OS
* That ts_sal is installed according SAL user guide instructions
* Running code in python 3.6.^ virtualenv # Carrot indicates any minor release in 3.6 should work tested with 3.6.3 and 3.6.2
* That ts_salobj code is located in gitrepo directory
* That ts_salobj is version 3.3.0

``` bash
   cd ~/gitrepo
   git clone https://github.com/lsst-ts/ts_CBP.git
   git clone https://github.com/lsst-ts/ts_salobj.git
   cd ts_salobj
   git checkout v3.3.0
   cd ~/gitrepo/ts_CBP
   virtualenv --python=python3 venv
   source venv/bin/activate
   source ~/gitrepo/ts_sal/setup.env
   pip install -e .
   export PYTHONPATH=$PYTHONPATH:~/gitrepo/ts_salobj/python
```

## Making Documentation

``` bash
   cd docs
   make html

```