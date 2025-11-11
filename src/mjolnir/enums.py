from enum import Enum


class HalterType(Enum):
    
    BARBELL = "barbell"
    EZ_CURL = "ez curl bar"
    DUMBELL = "dumbell"

ENUM_DICT = {
    "HalterType": HalterType,
    }