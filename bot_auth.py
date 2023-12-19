import datetime
from os import getenv

import pytz
from dotenv import load_dotenv
from jose import jwt


def create_token(d: dict):
    load_dotenv()
    token = None
    now = datetime.datetime.now(tz=pytz.utc)
    expires_at = now + datetime.timedelta(0, 30)  # 30 seconds
    d["expires_at"] = expires_at.strftime("%Y-%m-%dT%H:%M:%S%z")
    d["is_genuine"] = getenv("PEPPER")
    token = jwt.encode(d, getenv("SALT"), algorithm="HS256")
    return token
