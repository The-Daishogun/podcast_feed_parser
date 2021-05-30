import hashlib
from typing import Union


def hasher(data: Union[str, bytes], encoding: str = "utf-8"):
    if isinstance(data, str):
        data = data.encode(encoding=encoding)
    result = hashlib.md5(data)
    return result.hexdigest()
