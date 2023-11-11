"""The public package that holds the worldmaster apps.

This also imports the native modules.
"""

from ._worldmaster_rust import *

__doc__ = _worldmaster_rust.__doc__
if hasattr(_worldmaster_rust, "__all__"):
    __all__ = _worldmaster_rust.__all__
