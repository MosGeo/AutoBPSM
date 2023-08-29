import re
import hashlib
from uuid import uuid4


def generate_new_id(existing_ids: list[str] = []):
    """New curve id"""
    is_unique = False
    while not is_unique:
        new_id = str(uuid4())
        if new_id not in existing_ids:
            is_unique = True
    return new_id


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


def decode_id_and_name(id_name_string: str):
    id = None
    name = None
    if is_md5(id_name_string):
        id = id_name_string
    else:
        name = id_name_string
    return id, name


def items_lookup_return(items: list, is_unique: bool = True):
    """Returns one item and raises error if not found"""
    # Stopping condition
    if not is_unique:
        return items

    # One item setup
    n_items = len(items)
    if n_items == 0:
        raise LookupError("No item found")
    elif n_items == 1:
        return items[0]
    else:
        raise LookupError("Multiple items were found")


def num_string_convert(string: str) -> int | float | str:
    """Converts string if possible"""
    if string.isdigit():
        return int(string)
    elif float_string_check(string):
        return float(string)
    return string


def int_string_check(string: str) -> bool:
    """int check"""
    return string.isdigit()


def float_string_check(string: str) -> bool:
    """Float check"""
    try:
        float(string)
        return True
    except ValueError:
        return False
