from enum import Enum


class HalterType(Enum):
    
    BARBELL = "barbell"
    EZ_CURL = "ez curl bar"
    DUMBELL = "dumbell"

class OefeningBarbell(Enum):
    
    PRESS = "overhead press"
    SQUAT = "squat"
    BENCH = "bench press"
    DEADLIFT = "deadlift"

class OefeningType(Enum):
    
    LICHAAMSGEWICHT = 1
    GEWICHT = 2
    BARBELL = OefeningBarbell
    EZ_CURL = 4
    DUMBELL = 5

class RepetitieType(Enum):
    
    AANTAL = "aantal"
    BEREIK = "bereik"
    AMRAP = "amrap"
    BEREIK_AMRAP = "amrap met bereik"
    VRIJ = "vrij"

class SetType(Enum):
    
    GEWICHTLOOS = "gewichtloos"
    GEWICHT = "gewicht"
    PERCENTAGE = "percentage"

class SetGroepType(Enum):
    
    WARM_UP = "warm-up sets"
    HOOFD = "hoofdsets"
    AANVULLEND = "aanvullende sets"

ENUM_DICT = {
    "HalterType": HalterType,
    "SetGroepType": SetGroepType,
    }