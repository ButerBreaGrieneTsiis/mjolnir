from dataclasses import dataclass, field
from typing import Dict, List

from .enums import HalterType, OefeningType, RepetitieType, SetType, SetGroepType
from .register import GeregistreerdObject, Register

from grienetsiis import Decoder, openen_json, opslaan_json, invoer_validatie, invoer_kiezen


# @dataclass
# class Set:
    
#     repetities: int = field(default = 0)
#     rep_type: RepetitieType = field(default = RepetitieType.AANTAL)
#     set_type: SetType = field(default = SetType.GEWICHTLOOS)
#     massa: float = field(default = 0.0)
#     percentage: int  = field(default = 0)
    
#     def __repr__(self) -> str:
#         if self.set_type is SetType.GEWICHTLOOS:
#             return f"{self.repetities}"
#         elif self.set_type is SetType.GEWICHT:
#             return f"{self.repetities}@{self.massa}"
#         else:
#             return f"{self.repetities}@{self.percentage}%"

# @dataclass
# class Setgroep(GeregistreerdObject):
    
#     sets: List[Set]
    
#     @property
#     def naam(self):
#         return " ".join([set.__repr__() for set in self.sets])

# class Setgroepen(Register):
    
#     BESTANDSNAAM: str = "setgroepen"
#     TYPE: type = Setgroep

@dataclass
class Sjabloon(GeregistreerdObject):
    
    naam: str
    set_type: SetGroepType
    setgroepen: Dict[str, List[str]] = None
    
    def __repr__(self) -> str:
        return self.naam
    
    @classmethod
    def nieuw(
        cls,
        velden,
        ):
        
        cls = super().nieuw(velden)
        
        set_type = invoer_kiezen(
            beschrijving = "set type",
            keuzes = {set_type.value: set_type for set_type in SetType},
            )
        
        week_optie = invoer_kiezen(
            beschrijving = "hoeveel weken heeft dit sjabloon?",
            keuzes = {
                "1 week": 1,
                "2 weken": 2,
                "3 weken": 3,
                },
            )
        
        setgroepen = {}
        
        for week in range(1, week_optie + 1):
            
            sets = []
            
            print(f"\nkies de sets voor week {week}")
            
            while True:
                
                if len(sets) > 0:
                    
                    print("\nde huidige sets:")
                    [print(f"  {set}") for set in sets]
                    
                    if invoer_kiezen(
                        beschrijving = "nog een set toevoegen?",
                        keuzes = {"ja": False, "nee": True},
                        kies_een = False,
                        ):
                        
                        break
                
                repetitie_type = invoer_kiezen(
                    beschrijving = "repetitie type",
                    keuzes = {repetitie_type.value: repetitie_type for repetitie_type in RepetitieType},
                    )
                
                if repetitie_type == RepetitieType.VRIJ:
                    repetities = "?"
                elif repetitie_type == RepetitieType.AANTAL:
                    repetities = f"{invoer_validatie(
                        beschrijving = "aantal repetities",
                        type = int,
                        bereik = (1, 99),
                        )}"
                elif repetitie_type == RepetitieType.AMRAP:
                    repetities = f"{invoer_validatie(
                        beschrijving = "minimaal aantal repetities",
                        type = int,
                        bereik = (1, 99),
                        )}+"
                else:
                    repetities_minimaal = invoer_validatie(
                        beschrijving = "minimaal aantal repetities",
                        type = int,
                        bereik = (1, 99),
                        )
                    repetities_maximaal = invoer_validatie(
                        beschrijving = "maximaal aantal repetities",
                        type = int,
                        bereik = (1, 99),
                        )
                    
                    if repetitie_type == RepetitieType.BEREIK:
                        repetities = f"{repetities_minimaal}-{repetities_maximaal}"
                    else:
                        repetities = f"{repetities_minimaal}-{repetities_maximaal}+"
                
                if set_type == SetType.GEWICHTLOOS:
                    massa = ""
                elif set_type == SetType.GEWICHT:
                    massa = f"@{invoer_validatie(
                        beschrijving = "hoeveel massa",
                        type = float,
                        bereik = (1.0, 999.9),
                        )}"
                else:
                    massa = f"@{invoer_validatie(
                        beschrijving = "hoeveel percent",
                        type = int,
                        bereik = (0, 100),
                        )}%"
                
                aantal_sets = f"{invoer_validatie(
                    beschrijving = "aantal sets",
                    type = int,
                    bereik = (1, 10),
                    )}"
                
                if aantal_sets == "1":
                    set = f"{repetities}{massa}"
                else:
                    set = f"{aantal_sets}×{repetities}{massa}"
                
                sets.append(set)
            
            setgroepen[f"{week}"] = sets
        
        cls.setgroepen = setgroepen
        
        return cls

class Sjablonen(Register):
    
    BESTANDSNAAM: str = "sjablonen"
    TYPE: type = Sjabloon

# @dataclass
# class Oefening:
    
#     oefening: type[OefeningType]
#     setgroepen: List[Setgroep]

# @dataclass
# class TrainingsDag(GeregistreerdObject):
    
#     oefeningen: Dict[type[OefeningType], List[Set]]
    
#     # een blauwprint: lijst van oefeningen
#         # een oefening: deze <oefening> met een lijst van sets
#             # een set: aantal reps en (gewicht of percentage) -> TM zelf niet in dit bestand, dit is puur een blauwprint


# class TrainingsCyclus: # of TrainingsSchema
    
#     def __init__(
#         self,
#         naam: str,
#         weken: int,
#         dagen: int,
#         trainingsschemas: Dict[int, Dict[int, TrainingsDag]]
#         ) -> "TrainingsCyclus":
        
#         self.naam = naam
#         self.weken = weken
#         self.dagen = dagen
#         self.trainingsschemas = trainingsschemas

# class TrainingsCyci(Register):
    
#     BESTANDSNAAM: str = "trainingscycli"
#     TYPE: type = TrainingsCyclus


# # class TrainingsSuperCyclus: # of TrainingsSchema ?
    
# #     def __init__(
# #         self,
# #         cycli: List[TrainingsCyclus] = None,
# #         ) -> TrainingsSuperCyclus:
        
# #         self.cycli = cycli


# SETGROEPEN = Setgroepen.openen()
# SJABLONEN = Sjablonen.openen()