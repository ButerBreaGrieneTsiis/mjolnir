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
    
    PUSH_UPS = ("push-up", [Spiergroep.BORST, Spiergroep.SCHOUDERS, Spiergroep.TRICEPS])
    BENCH_DIPS = ("bench dips", [Spiergroep.TRICEPS])
    SIT_UPS = ("sit-ups", [Spiergroep.BUIKSPIEREN])
    PULL_UPS = ("pull-up", [Spiergroep.BOVENRUG, Spiergroep.ONDERARMEN])
    CHIN_UPS = ("chin-up", [Spiergroep.BICEPS, Spiergroep.BOVENRUG, Spiergroep.ONDERARMEN])
    AB_WHEEL = ("ab wheel", [Spiergroep.BUIKSPIEREN])
    PLANKS = ("planks", [Spiergroep.BUIKSPIEREN])

class OefeningGewicht(OefeningEnum):
    
    SIT_UPS_GEWICHT = ("sit-ups met gewicht", [Spiergroep.BUIKSPIEREN])
    LATERAL_RAISE = ("lateral raise", [Spiergroep.SCHOUDERS])

class OefeningBarbell(OefeningEnum):
    
    PRESS = ("overhead press", [Spiergroep.SCHOUDERS])
    SQUAT = ("squat", [Spiergroep.ONDERRUG, Spiergroep.BILLEN, Spiergroep.QUADRICEPS, Spiergroep.HAMSTRINGS])
    BENCH = ("bench press", [Spiergroep.BORST, Spiergroep.TRICEPS])
    DEADLIFT = ("deadlift", [Spiergroep.ONDERRUG, Spiergroep.BILLEN, Spiergroep.QUADRICEPS, Spiergroep.HAMSTRINGS])
    BENT_OVER_ROW = ("bent-over row", [Spiergroep.BOVENRUG])
    SHRUG = ("shrug", [Spiergroep.BOVENRUG])
    CALF_RAISE = ("calf raise", [Spiergroep.KUITEN])

class OefeningCurl(OefeningEnum):
    
    CURLS = ("curls", [Spiergroep.BICEPS])

class OefeningDumbbell(OefeningEnum):
    
    ...

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
    AMSAP = "amsap"
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