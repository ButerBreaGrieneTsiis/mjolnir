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

class Oefening(Enum):
    pass

class OefeningLichaamsgewicht(Oefening):
    
    PUSH_UPS = "push-up"
    BENCH_DIPS = "bench dips"
    SIT_UPS = "sit-ups"
    PULL_UPS = "pull-up"
    CHIN_UPS = "chin-up"

class OefeningGewicht(Oefening):
    
    SIT_UPS_GEWICHT = "sit-ups met gewicht"

class OefeningBarbell(Oefening):
    
    PRESS = "overhead press"
    SQUAT = "squat"
    BENCH = "bench press"
    DEADLIFT = "deadlift"
    BENT_OVER_ROW = "bent-over row"
    SHRUG = "shrug"
    CALF_RAISE = "calf raise"

class OefeningCurl(Oefening):
    
    CURLS = "curls"

class OefeningDumbbell(Oefening):
    
    LATERAL_RAISE = "lateral raise"

class OefeningType(Enum):
    
    LICHAAMSGEWICHT = ("lichaamsgewicht", OefeningLichaamsgewicht)
    GEWICHT = ("gewicht", OefeningGewicht)
    BARBELL = ("barbell", OefeningBarbell)
    EZ_CURL = ("ez curl", OefeningCurl)
    DUMBBELL = ("dumbbell", OefeningDumbbell)

class RepetitieType(Enum):
    
    AANTAL = "aantal"
    BEREIK = "bereik"
    AMRAP = "amrap"
    BEREIK_AMRAP = "amrap met bereik"
    VRIJ = "vrij"

class GewichtType(Enum):
    
    GEWICHTLOOS = "gewichtloos"
    GEWICHT = "gewicht"
    PERCENTAGE = "percentage"

class SetType(Enum):
    
    OPWARMEN = "opwarmsets"
    HOOFD = "hoofdsets"
    AANVULLEND = "aanvullende sets"
    VRIJ = "vrij"
    

ENUM_DICT = {
    "HalterType": HalterType,
    "OefeningLichaamsgewicht": OefeningLichaamsgewicht,
    "OefeningGewicht": OefeningGewicht,
    "OefeningBarbell": OefeningBarbell,
    "OefeningCurl": OefeningCurl,
    "OefeningDumbbell": OefeningDumbbell,
    "OefeningType": OefeningType,
    "RepetitieType": RepetitieType,
    "GewichtType": GewichtType,
    "SetType": SetType,
    }