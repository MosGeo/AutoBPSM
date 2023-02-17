import re
import hashlib


def is_md5(hash: str) -> bool:
    """Check if a string is md5"""
    pattern = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    match = re.fullmatch(pattern, hash)
    is_matched = match is not None
    return is_matched


def md5(input: str) -> str:
    """Generates and md5 hash given an input string"""
    input_encoded = input.encode("utf-8")
    md5_hash = hashlib.md5()
    md5_hash.update(input_encoded)
    hash = md5_hash.hexdigest()
    hash = f"{hash[0:8]}-{hash[8:12]}-{hash[12:16]}-{hash[16:20]}-{hash[20:]}"
    return hash
