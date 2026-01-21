from enum import Enum
from typing import List


class HalterType(Enum):
    
    BARBELL = "barbell"
    EZ_CURL = "ez curl bar"
    DUMBELL = "dumbell"

class GewichtType(Enum):
    
    GEWICHTLOOS = "gewichtloos"
    GEWICHT = "gewicht"
    PERCENTAGE = "percentage"
    VRIJ = "vrij"

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

class OefeningType(Enum):
    
    def __new__(
        cls,
        naam: str,
        gewicht_types: List[GewichtType],
        halter_type: HalterType | None = None,
        ):
        
        oefening_type = object.__new__(cls)
        oefening_type._value = naam
        oefening_type.gewicht_types = gewicht_types
        oefening_type.halter_type = halter_type
        return oefening_type
    
    LICHAAMSGEWICHT = "lichaamsgewicht", [GewichtType.GEWICHTLOOS]
    GEWICHT = "gewicht", [GewichtType.GEWICHT, GewichtType.VRIJ]
    BARBELL = "barbell",  [GewichtType.GEWICHT, GewichtType.PERCENTAGE, GewichtType.VRIJ], HalterType.BARBELL
    EZ_CURL = "ez curl",  [GewichtType.GEWICHT, GewichtType.VRIJ], HalterType.EZ_CURL
    DUMBBELL = "dumbbell", [GewichtType.GEWICHT, GewichtType.VRIJ], HalterType.DUMBELL
    
    @property
    def naam(self) -> str:
        return self._value
    
    @property
    def gewichtloos(self) -> bool:
        return self == OefeningType.LICHAAMSGEWICHT

class Oefening(Enum):
    
    def __new__( # https://stackoverflow.com/questions/75384124
        cls,
        naam: str,
        spiergroepen: List[Spiergroep],
        oefening_type: OefeningType,
        dextraal: bool = False,
        ):
        
        oefening = object.__new__(cls)
        oefening._value = naam
        oefening.spiergroepen = spiergroepen
        oefening.oefening_type = oefening_type
        oefening.dextraal = dextraal
        return oefening
    
    # lichaamsgewicht
    PUSH_UPS = "push-up", [Spiergroep.BORST, Spiergroep.SCHOUDERS, Spiergroep.TRICEPS], OefeningType.LICHAAMSGEWICHT
    BENCH_DIPS = "bench dips", [Spiergroep.TRICEPS], OefeningType.LICHAAMSGEWICHT
    SIT_UPS = "sit-ups", [Spiergroep.BUIKSPIEREN], OefeningType.LICHAAMSGEWICHT
    PULL_UPS = "pull-up", [Spiergroep.BOVENRUG, Spiergroep.ONDERARMEN], OefeningType.LICHAAMSGEWICHT
    CHIN_UPS = "chin-up", [Spiergroep.BICEPS, Spiergroep.BOVENRUG, Spiergroep.ONDERARMEN], OefeningType.LICHAAMSGEWICHT
    AB_WHEEL = "ab wheel", [Spiergroep.BUIKSPIEREN], OefeningType.LICHAAMSGEWICHT
    PLANKS = "planks", [Spiergroep.BUIKSPIEREN], OefeningType.LICHAAMSGEWICHT
    
    # gewicht
    SIT_UPS_GEWICHT = "sit-ups met gewicht", [Spiergroep.BUIKSPIEREN], OefeningType.GEWICHT
    LATERAL_RAISE = "lateral raise", [Spiergroep.SCHOUDERS], OefeningType.GEWICHT, True
    
    # barbell
    PRESS = "overhead press", [Spiergroep.SCHOUDERS], OefeningType.BARBELL
    SQUAT = "squat", [Spiergroep.ONDERRUG, Spiergroep.BILLEN, Spiergroep.QUADRICEPS, Spiergroep.HAMSTRINGS], OefeningType.BARBELL
    BENCH = "bench press", [Spiergroep.BORST, Spiergroep.TRICEPS], OefeningType.BARBELL
    DEADLIFT = "deadlift", [Spiergroep.ONDERRUG, Spiergroep.BILLEN, Spiergroep.QUADRICEPS, Spiergroep.HAMSTRINGS], OefeningType.BARBELL
    BENT_OVER_ROW = "bent-over row", [Spiergroep.BOVENRUG], OefeningType.BARBELL
    SHRUG = "shrug", [Spiergroep.BOVENRUG], OefeningType.BARBELL
    CALF_RAISE = "calf raise", [Spiergroep.KUITEN], OefeningType.BARBELL
    
    # ez-curl
    CURLS = "curls", [Spiergroep.BICEPS], OefeningType.EZ_CURL
    
    @property
    def naam(self) -> str:
        return self._value
    
    @property
    def naam_underscore(self) -> str:
        return self._value.replace(" ", "_")
    
    @property
    def gewicht_types(self) -> List[GewichtType]:
        return self.oefening_type.gewicht_types
    
    @property
    def gewichtloos(self) -> bool:
        return self.oefening_type.gewichtloos
    
    @property
    def halter_type(self) -> HalterType | None:
        return self.oefening_type.halter_type
    
class Status(Enum):
    
    GEPLAND = "gepland"
    HUIDIG = "huidig"
    AFGEROND = "afgerond"
    AFGEBROKEN = "afgebroken"

ENUMS = {
    "HalterType": HalterType,
    "GewichtType": GewichtType,
    "RepetitieType": RepetitieType,
    "SetType": SetType,
    "SetGroepType": SetGroepType,
    "OefeningType": OefeningType,
    "Oefening": Oefening,
    "Status": Status,
    }