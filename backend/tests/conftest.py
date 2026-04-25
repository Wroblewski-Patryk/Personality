import os
import platform
from collections import namedtuple


if os.name == "nt":
    machine = os.environ.get("PROCESSOR_ARCHITECTURE", "AMD64")
    processor = os.environ.get("PROCESSOR_IDENTIFIER", machine)
    UnameResult = namedtuple("uname_result", "system node release version machine processor")
    cached_uname = UnameResult("Windows", "", "", "", machine, processor)

    platform.machine = lambda: machine
    platform.uname = lambda: cached_uname
    platform._uname_cache = cached_uname
