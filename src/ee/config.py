import os

EE_DEBUG = os.getenv("EE_DEBUG", "0") == "1"

EE_REQUEST_TIMEOUT = int(os.getenv("EE_REQUEST_TIMEOUT", "5"))  # seconds
