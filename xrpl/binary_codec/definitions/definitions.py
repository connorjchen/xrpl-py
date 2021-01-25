"""Maps and helpers providing serialization-related information about fields."""

import json
import os
from typing import Any, Dict, Tuple

from xrpl.binary_codec.definitions.field_header import FieldHeader
from xrpl.binary_codec.definitions.field_info import FieldInfo
from xrpl.binary_codec.definitions.field_instance import FieldInstance
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException


def load_definitions(filename: str = "definitions.json") -> Dict[str, Any]:
    """
    Loads JSON from the definitions file and converts it to a preferred format.
    The definitions file contains information required for the XRP Ledger's
    canonical binary serialization format:
    `Serialization <https://xrpl.org/serialization.html>`_

    :param filename: The name of the definitions file.
    (The definitions file should be drop-in compatible with the one from the
    ripple-binary-codec JavaScript package.)
    :return: A dictionary containing the mappings provided in the definitions file.
    """
    dirname = os.path.dirname(__file__)
    absolute_path = os.path.join(dirname, filename)
    with open(absolute_path) as definitions_file:
        definitions = json.load(definitions_file)
        return {
            "TYPES": definitions["TYPES"],
            # type_name str: type_sort_key int
            "FIELDS": {
                k: v for (k, v) in definitions["FIELDS"]
            },  # convert list of tuples to dict
            # "field_name" str: {
            #   "nth": field_sort_key int,
            #   "isVLEncoded": bool,
            #   "isSerialized": bool,
            #   "isSigningField": bool,
            #   "type": string
            # }
            "LEDGER_ENTRY_TYPES": definitions["LEDGER_ENTRY_TYPES"],
            "TRANSACTION_RESULTS": definitions["TRANSACTION_RESULTS"],
            "TRANSACTION_TYPES": definitions["TRANSACTION_TYPES"],
        }


DEFINITIONS = load_definitions()
TRANSACTION_TYPE_CODE_TO_STR_MAP = {
    value: key for (key, value) in DEFINITIONS["TRANSACTION_TYPES"].items()
}
TRANSACTION_RESULTS_CODE_TO_STR_MAP = {
    value: key for (key, value) in DEFINITIONS["TRANSACTION_RESULTS"].items()
}

TYPE_ORDINAL_MAP = DEFINITIONS["TYPES"]

FIELD_INFO_MAP = {}
FIELD_HEADER_NAME_MAP: Dict[FieldHeader, str] = {}

# Populate FIELD_INFO_MAP and FIELD_HEADER_NAME_MAP
try:
    for field in DEFINITIONS["FIELDS"]:
        field_entry = DEFINITIONS["FIELDS"][field]
        field_info = FieldInfo(
            field_entry["nth"],
            field_entry["isVLEncoded"],
            field_entry["isSerialized"],
            field_entry["isSigningField"],
            field_entry["type"],
        )
        header = FieldHeader(TYPE_ORDINAL_MAP[field_entry["type"]], field_entry["nth"])
        FIELD_INFO_MAP[field] = field_info
        FIELD_HEADER_NAME_MAP[header] = field
except KeyError as e:
    raise XRPLBinaryCodecException(
        "Malformed definitions.json file. (Original exception: KeyError: {})".format(e)
    )


def get_field_type_name(field_name: str) -> str:
    """
    Returns the serialization data type for the given field name.
    `Serialization Type List <https://xrpl.org/serialization.html#type-list>`_
    """
    return FIELD_INFO_MAP[field_name].type


def get_field_type_code(field_name: str) -> int:
    """
    Returns the type code associated with the given field.
    `Serialization Type Codes <https://xrpl.org/serialization.html#type-codes>`_
    """
    field_type_name = get_field_type_name(field_name)
    field_type_code = TYPE_ORDINAL_MAP[field_type_name]
    if not isinstance(field_type_code, int):
        raise XRPLBinaryCodecException(
            "Field type codes in definitions.json must be ints."
        )

    return field_type_code


def get_field_code(field_name: str) -> int:
    """
    Returns the field code associated with the given field.
    `Serialization Field Codes <https://xrpl.org/serialization.html#field-codes>`_
    """
    return FIELD_INFO_MAP[field_name].nth


# TODO: may be able to remove this method,
#  since a FieldHeader object provides this info.
def get_field_sort_key(field_name: str) -> Tuple[int, int]:
    """
    Returns a tuple sort key for a given field name.
    `Serialization Canonical Field Order
    <https://xrpl.org/serialization.html#canonical-field-order>`_
    """
    return get_field_type_code(field_name), get_field_code(field_name)


def get_field_header_from_name(field_name: str) -> FieldHeader:
    """Returns a FieldHeader object for a field of the given field name."""
    return FieldHeader(get_field_type_code(field_name), get_field_code(field_name))


def get_field_name_from_header(field_header: FieldHeader) -> str:
    """Returns the field name described by the given FieldHeader object."""
    return FIELD_HEADER_NAME_MAP[field_header]


def get_field_instance(field_name: str) -> FieldInstance:
    """Return a FieldInstance object for the given field name."""
    info = FIELD_INFO_MAP[field_name]
    field_header = get_field_header_from_name(field_name)
    return FieldInstance(
        info,
        field_name,
        field_header,
    )
