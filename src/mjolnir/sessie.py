import datetime as dt
from enum import Enum
from typing import Dict, List, Union

from .enums import OefeningEnum


class Set:
    
    repetities: int
    gewicht: float = None
    
    @property
    def volume(self) -> float:
        ...

class Oefening:
    
    oefening: OefeningEnum
    sets: Dict[str, List[Set]] # waar str = SetGroepType.value
    
    @property
    def volume(self) -> float:
        ...

class Sessie:
    
    schema_uuid: str
    week: int
    dag: int
    datum: dt.date
    oefeningen: List[Oefening] = None
    
    def opslaan(self) -> None:
        ...
        # opslaan van deze sessie na afronden dashboard
        # schema_uuid:
        # week:
        # dag:
        # datum:
        # oefeningen:
        #   oefening 1:
        #     OefeningEnum
        #     setgroep 1: (ook al is er geen setgroep, bijv. bij assistance, alsnog setgroep "overig")
        #       set 1:
        #         repetities: int # enkel repetities gedaan, repetities gepland volgt wel uit schema_uuid
        #         (gewicht: float) indien toepasselijk # enkel gewicht gedaan, gewicht gepland volgt wel uit schema_uuid
        #       set 2: # enkel sets gedaan, sets gepland volgt wel uit schema_uuid
        #       :
        #     setgroep 2:
        #     :
        #   oefening 2:
        #   :
        #
        
        
        # koppeling van de HalterType vindt op de achtergrond plaats:
        # oefening is gelinkt aan een HalterType
        # indien meerdere HalterTypes gedefinieerd zijn, is op het dashboard een keuze te maken (voor nu nog niet nodig om te implementeren)