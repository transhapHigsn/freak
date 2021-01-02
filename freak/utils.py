from typing import List

from hashlib import md5


def generate_hash_for_path(path: List[str]) -> str:
    stringify_path = str(path).encode("utf-8")
    return md5(string=stringify_path).hexdigest()
