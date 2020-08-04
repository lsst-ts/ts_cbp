"""This package contains both the component and CSC logic for CBP.

"""

from . import csc, component, version
from .csc import *
from .component import *

try:
    from .version import *
except ImportError:
    __version__ = "?"
