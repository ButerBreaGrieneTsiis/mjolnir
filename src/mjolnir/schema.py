from dataclasses import dataclass
import datetime as dt
from typing import ClassVar, Dict, List

from mjolnir.enums import OefeningType, RepetitieType, GewichtType, SetType, OefeningEnum, Status, SetGroepType
from mjolnir.register import GeregistreerdObject, Register

from grienetsiis import invoer_validatie, invoer_kiezen


@dataclass
class Sjabloon(GeregistreerdObject):
    
    naam: str
    setgroep_type: SetGroepType
    weken: int = 0
    sets: Dict[str, List[str]] = None
    
    BESTANDSNAAM: ClassVar[str] = "sjablonen"
    
    def __repr__(self) -> str:
        return self.naam
    
    @classmethod
    def nieuw(
        cls,
        velden,
        ):
        
        cls = super().nieuw(velden)
        
        def sets_maken() -> List[str]:
            
            sets = []
            
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
                    repetitie_tekst = "?"
                elif repetitie_type == RepetitieType.AANTAL:
                    repetitie_tekst = f"{invoer_validatie(
                        beschrijving = "aantal repetities",
                        type = int,
                        bereik = (1, 99),
                        )}"
                elif repetitie_type == RepetitieType.AMRAP:
                    repetitie_tekst = f"{invoer_validatie(
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
                        repetitie_tekst = f"{repetities_minimaal}-{repetities_maximaal}"
                    else:
                        repetitie_tekst = f"{repetities_minimaal}-{repetities_maximaal}+"
                
                gewicht_type = invoer_kiezen(
                    beschrijving = "gewicht type",
                    keuzes = {gewicht_type.value: gewicht_type for gewicht_type in GewichtType},
                    )
                
                if gewicht_type == GewichtType.GEWICHTLOOS:
                    massa = ""
                elif gewicht_type == GewichtType.GEWICHT:
                    massa = f"@{invoer_validatie(
                        beschrijving = "hoeveel massa",
                        type = float,
                        bereik = (1.0, 999.9),
                        )}"
                elif gewicht_type == GewichtType.VRIJ:
                    massa = "@?"
                else:
                    massa = f"@{invoer_validatie(
                        beschrijving = "hoeveel percent",
                        type = int,
                        bereik = (0, 100),
                        )}%"
                
                set_type = invoer_kiezen(
                    beschrijving = "set type",
                    keuzes = {set_type.value: set_type for set_type in SetType},
                    )
                
                aantal_sets = invoer_validatie(
                    beschrijving = "aantal sets",
                    type = int,
                    bereik = (1, 10),
                    )
                
                if set_type == SetType.AANTAL:
                    set_tekst = f"{aantal_sets}x"
                else:
                    set_tekst = f"{aantal_sets}+x"
                    
                if aantal_sets == "1":
                    set = f"{repetitie_tekst}{massa}"
                else:
                    set = f"{set_tekst}{repetitie_tekst}{massa}"
                
                sets.append(set)
                
            return sets
        
        weken = invoer_kiezen(
            beschrijving = "hoeveel weken heeft dit sjabloon?",
            keuzes = {
                "weekonafhankelijk": 0,
                "1 week": 1,
                "2 weken": 2,
                "3 weken": 3,
                },
            )
        
        sets_per_week = {}
        
        if weken == 0:
            print(f"\nkies de sets voor elke week")
            sets = sets_maken()
            sets_per_week[f"week {weken}"] = sets
        else:
            for week in range(1, weken + 1):
                
                print(f"\nkies de sets voor week {week}")
                sets = sets_maken()
                sets_per_week[f"week {week}"] = sets
        
        cls.weken = weken
        cls.sets = sets_per_week
        
        return cls

# @dataclass
# class SchemaDag(GeregistreerdObject):
    
#     week: int
#     dag: int
#     oefeningen: List
#     afgerond: bool = False

@dataclass
class Schema(GeregistreerdObject):
    
    naam: str
    weken: int
    dagen: int
    status: Status = Status.GEPLAND # status wordt veranderd naar HUIDIG indien dit de eerstvolgende geplande is, en er zijn geen HUIDIG aanwezig
    trainingsschema: Dict[int, Dict[str, List[Sjabloon]]] = None
    trainingsgewichten: List[Dict[str, OefeningEnum | float]] = None
    datum_start: dt.date = None
    datum_eind: dt.date = None
    
    BESTANDSNAAM: ClassVar[str] = "schema"
    
    @classmethod
    def nieuw(
        cls,
        velden,
        ) -> "Schema":
        
        cls = super().nieuw(velden)
        
        trainingsschema = {}
        trainingsgewichten = []
        
        for dag in range(1, cls.dagen + 1):
            
            trainingsschema[f"dag {dag}"] = []
            
            print(f"\ntoevoegen oefeningen voor dag {dag}")
            
            while True:
                
                if len(trainingsschema[f"dag {dag}"]) > 0:
                    print(f"\nschema voor dag {dag}")
                    for oefening_sjablonen in trainingsschema[f"dag {dag}"]:
                        print(f"  oefening \"{oefening_sjablonen["oefening"].value[0]}\"")
                        for sjabloon_uuid in oefening_sjablonen["sjablonen"]:
                            print(f"    {Register().sjablonen[sjabloon_uuid]}")
                    
                    if invoer_kiezen(
                        beschrijving = "nog een oefening toevoegen?",
                        keuzes = {"ja": False, "nee": True},
                        kies_een = False,
                        ):
                        
                        break
                
                oefening_type = invoer_kiezen(
                    beschrijving = "oefeningstype",
                    keuzes = {enum.value[0]: enum.value[1] for enum in OefeningType},
                    )
                
                oefening = invoer_kiezen(
                    beschrijving = "oefening",
                    keuzes = {enum.value[0]: enum for enum in oefening_type},
                    )
                
                print(f"\n>>> oefening \"{oefening.value[0]}\" gekozen")
                
                oefening_sjablonen = {
                    "oefening": oefening,
                    "sjablonen": [],
                    }
                
                while True:
                    
                    if len(oefening_sjablonen["sjablonen"]) > 0:
                        print(f"\nsjablonen voor {oefening.value}")
                        for sjabloon_uuid in oefening_sjablonen["sjablonen"]:
                            print(f"    {Register().sjablonen[sjabloon_uuid]}")
                        
                        if invoer_kiezen(
                            beschrijving = "nog een sjabloon toevoegen?",
                            keuzes = {"ja": False, "nee": True},
                            kies_een = False,
                            ):
                            
                            break
                    
                    sjabloon_uuid = Register().sjablonen.filter(weken = [0, cls.weken]).kiezen()
                    
                    oefening_sjablonen["sjablonen"].append(sjabloon_uuid)
                    
                    if any(["%" in set for week in Register().sjablonen[sjabloon_uuid].sets.values() for set in week]):
                        
                        if not any([oefening == trainingsgewicht["oefening"] for trainingsgewicht in trainingsgewichten]):
                        
                            print(f"\ntrainingspercentage nodig voor oefening \"{oefening.value[0]}\"")
                            
                            trainingsgewicht = invoer_validatie(
                                f"trainingsgewicht",
                                type = float,
                                )
                            
                            trainingsgewichten.append({
                                "oefening": oefening,
                                "trainingsgewicht": trainingsgewicht,
                                })
                
                trainingsschema[f"dag {dag}"].append(oefening_sjablonen)
        
        cls.trainingsschema = trainingsschema
        cls.trainingsgewichten = trainingsgewichten
        
        return cls
        
        # bool: zijn de oefeningen gelijk per week (voor nu enkel True)
        
        # voeg oefeningen toe voor de dagen:
            # dag 1:
                # oefening 1
                    # kies een oefening -> OefeningType -> Oefening (bijv. OefeningType.BARBELL -> OefeningBarbell.PRESS)
                    # sjablonen kiezen (enkel sjablonen tonen met overeenkomstig aantal weken)
                        #   sjabloon 1
                        #   sjabloon 2
                        #   sjabloon :
                    # volgende oefening?
                # oefening 2
                # oefening : (hoe omgaan bij bijv. sit-ups met selecteren sjabloon als de reps/sets minder strak bepaald zijn?)
                # volgende dag?
            # dag 2
            # dag :
        
        # opstellen SchemaDag voor elke dag
        
        # het paneel opent in principe het Schema object 
        # en pakt dan de eerstvolgende SchemaDag die isafgerond = False
        
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

Register.DECODERS["sjablonen"] = {
    "class": Sjabloon,
    "decoder_functie": Sjabloon.van_json,
    }
Register.ENCODERS["sjablonen"] = {
    "class": Sjabloon,
    "encoder_functie": Sjabloon.naar_json,
    }
Register.DECODERS["schema"] = {
    "class": Schema,
    "decoder_functie": Schema.van_json,
    }
Register.ENCODERS["schema"] = {
    "class": Schema,
    "encoder_functie": Schema.naar_json,
    }