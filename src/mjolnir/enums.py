from enum import Enum


class HalterType(Enum):
    
    BARBELL = "barbell"
    EZ_CURL = "ez curl bar"
    DUMBELL = "dumbell"

class Spiergroep(Enum):
    
    BORST = "borst"
    BOVENRUG = "bovenrug"
    SCHOUDERS = "schouder"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    ONDERARMEN = "onderarmen"
    BUIKSPIEREN = "buikspieren"
    ONDERRUG = "onderrug"
    BILLEN = "billen"
    QUADRICEPS = "quadriceps"
    HAMSTRINGS = "hamstrings"
    KUITEN = "kuiten"

class OefeningEnum(Enum):
    pass

class OefeningLichaamsgewicht(OefeningEnum):
    
    PUSH_UPS = ("push-up", [])
    BENCH_DIPS = ("bench dips", [])
    SIT_UPS = ("sit-ups", [])
    PULL_UPS = ("pull-up", [])
    CHIN_UPS = ("chin-up", [])

class OefeningGewicht(OefeningEnum):
    
    SIT_UPS_GEWICHT = ("sit-ups met gewicht", [])

class OefeningBarbell(OefeningEnum):
    
    PRESS = ("overhead press", [Spiergroep.SCHOUDERS])
    SQUAT = ("squat", [Spiergroep.ONDERRUG, Spiergroep.BILLEN, Spiergroep.QUADRICEPS, Spiergroep.HAMSTRINGS])
    BENCH = ("bench press", [])
    DEADLIFT = ("deadlift", [])
    BENT_OVER_ROW = ("bent-over row", [])
    SHRUG = ("shrug", [])
    CALF_RAISE = ("calf raise", [])

class OefeningCurl(OefeningEnum):
    
    CURLS = ("curls", [])

class OefeningDumbbell(OefeningEnum):
    
    LATERAL_RAISE = ("lateral raise", [])

class GewichtType(Enum):
    
    GEWICHTLOOS = "gewichtloos"
    GEWICHT = "vast"
    PERCENTAGE = "percentage"
    VRIJ = "vrij"

class OefeningType(Enum):
    
    LICHAAMSGEWICHT = ("lichaamsgewicht", OefeningLichaamsgewicht, [GewichtType.GEWICHTLOOS])
    GEWICHT = ("gewicht", OefeningGewicht, [GewichtType.GEWICHT, GewichtType.VRIJ])
    BARBELL = ("barbell", OefeningBarbell, [GewichtType.GEWICHT, GewichtType.PERCENTAGE, GewichtType.VRIJ])
    EZ_CURL = ("ez curl", OefeningCurl, [GewichtType.GEWICHT, GewichtType.VRIJ])
    DUMBBELL = ("dumbbell", OefeningDumbbell, [GewichtType.GEWICHT, GewichtType.VRIJ])

class RepetitieType(Enum):
    
    AANTAL = "aantal"
    BEREIK = "bereik"
    AMRAP = "amrap"
    BEREIK_AMRAP = "amrap met bereik"
    VRIJ = "vrij"

class SetType(Enum):
    
    AANTAL = "aantal"
    BEREIK = "bereik"
    AMSAP = "amsap"
    BEREIK_AMSAP = "amsap met bereik"
    VRIJ = "vrij"

class SetGroepType(Enum):
    
    OPWARMEN = "opwarmsets"
    HOOFD = "hoofdsets"
    AANVULLEND = "aanvullende sets"
    OVERIG = "overig"

class Status(Enum):
    
    GEPLAND = "gepland"
    HUIDIG = "huidig"
    AFGEROND = "afgerond"
    AFGEBROKEN = "afgebroken"

ENUMS = {
    "HalterType": HalterType,
    "OefeningLichaamsgewicht": OefeningLichaamsgewicht,
    "OefeningGewicht": OefeningGewicht,
    "OefeningBarbell": OefeningBarbell,
    "OefeningCurl": OefeningCurl,
    "OefeningDumbbell": OefeningDumbbell,
    "OefeningType": OefeningType,
    "GewichtType": GewichtType,
    "RepetitieType": RepetitieType,
    "SetType": SetType,
    "SetGroepType": SetGroepType,
    "Status": Status,
    }

HALTERS = {
    "OefeningBarbell": HalterType.BARBELL,
    "OefeningCurl": HalterType.EZ_CURL,
    "OefeningDumbbell": HalterType.DUMBELL,
    }