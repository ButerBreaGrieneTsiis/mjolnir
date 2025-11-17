from enum import Enum


class Eenheid(Enum):
    
    KILOGRAM = "kg", "kilogram"
    REPETITIES = "reps", "repetities"
    
    def __new__(cls, enkelvoud, meervoud):
        veld = object.__new__(cls)
        veld._value_    = enkelvoud
        veld.enkelvoud  = enkelvoud
        veld.meervoud   = meervoud
        return veld

class Hoeveelheid:
    
    VELDEN = frozenset((
        "waarde",
        "eenheid",
        ))
    
    def __init__(
        self,
        waarde: float,
        eenheid: Eenheid,
        ) -> "Hoeveelheid":
        
        self.waarde = waarde
        self.eenheid = eenheid
    
    def __repr__(self) -> str:
        
        eenheid = self.eenheid.enkelvoud if self.waarde == 1.0 else self.eenheid.meervoud
        
        return f"{f"{self.waarde:.1f}".rstrip("0").rstrip(".")} {eenheid}"