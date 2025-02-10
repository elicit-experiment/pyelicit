"""
Elicit client module for Python
"""

import sys
import collections

if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    from collections.abc import MutableMapping
    from collections.abc import Mapping
    # hack to get pyswagger to work on python 3.11
    setattr(collections, "MutableMapping", collections.abc.MutableMapping)
    setattr(collections, "Mapping", collections.abc.Mapping)

from . import elicit
from . import api
from . import command_line
