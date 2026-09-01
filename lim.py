import os
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

if os.getenv("TESTING") == "1":
    limiter.enabled = False