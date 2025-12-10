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
    gewicht_type: GewichtType
    set_type: SetType
    weken: int = 0
    sets: Dict[str, List[str]] = None
    
    BESTANDSNAAM: ClassVar[str] = "sjablonen"
    
    def __repr__(self) -> str:
        return f"{self.naam} (setgroep \"{self.setgroep_type.value}\", gewichttype \"{self.gewicht_type.value}\")"
    
    @classmethod
    def nieuw(
        cls,
        velden,
        ):
        
        cls = super().nieuw(velden)
        
        def sets_maken(
            gewicht_type: GewichtType,
            set_type: SetType,
            ) -> List[str]:
            
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
                
                if set_type == SetType.VRIJ:
                    set_tekst = "?x"
                elif set_type == SetType.AANTAL:
                    set_tekst = f"{invoer_validatie(
                        beschrijving = "aantal sets",
                        type = int,
                        bereik = (1, 10),
                        )}x"
                else:
                    set_tekst = f"{invoer_validatie(
                        beschrijving = "minimaal aantal sets",
                        type = int,
                        bereik = (1, 99),
                        )}+x"
                
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
                
                if set_tekst == "1x":
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
            sets = sets_maken(cls.gewicht_type, cls.set_type)
            sets_per_week[f"week {weken}"] = sets
        else:
            for week in range(1, weken + 1):
                
                print(f"\nkies de sets voor week {week}")
                sets = sets_maken(cls.gewicht_type, cls.set_type)
                sets_per_week[f"week {week}"] = sets
        
        cls.weken = weken
        cls.sets = sets_per_week
        
        return cls

@dataclass
class Schema(GeregistreerdObject):
    
    naam: str
    weken: int
    dagen: int
    status: Status = Status.GEPLAND
    datum_begin: dt.date = None
    datum_eind: dt.date = None
    oefeningen: Dict[str, Dict[str, List[Sjabloon]]] = None
    trainingsgewichten: List[Dict[str, OefeningEnum | float]] = None
    sessies: Dict[str, Dict[str, dt.date]] = None
    
    BESTANDSNAAM: ClassVar[str] = "schema"
    
    def __repr__(self) -> str:
        return f"{self.naam} ({self.status.value})"
    
    @classmethod
    def nieuw(
        cls,
        velden,
        ) -> "Schema":
        
        cls = super().nieuw(velden)
        
        oefeningen = {}
        trainingsgewichten = []
        sessies = {}
        
        for week in range(1, cls.weken + 1):
            sessies[f"week {week}"] = {}
            for dag in range(1, cls.dagen + 1):
                sessies[f"week {week}"][f"dag {dag}"] = {
                    "datum": None,
                    "status": Status.GEPLAND,
                    }
        
        for dag in range(1, cls.dagen + 1):
            
            oefeningen[f"dag {dag}"] = []
            
            print(f"\ntoevoegen oefeningen voor dag {dag}")
            
            while True:
                
                if len(oefeningen[f"dag {dag}"]) > 0:
                    print(f"\nschema voor dag {dag}")
                    for oefening_sjablonen in oefeningen[f"dag {dag}"]:
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
                    keuzes = {enum.value[0]: enum for enum in OefeningType},
                    )
                
                oefening = invoer_kiezen(
                    beschrijving = "oefening",
                    keuzes = {enum.value[0]: enum for enum in oefening_type.value[1]},
                    )
                
                print(f"\n>>> oefening \"{oefening.value[0]}\" gekozen")
                
                oefening_sjablonen = {
                    "oefening": oefening,
                    "sjablonen": [],
                    }
                
                while True:
                    
                    if len(oefening_sjablonen["sjablonen"]) > 0:
                        print(f"\nsjablonen voor {oefening.value[0]}")
                        for sjabloon_uuid in oefening_sjablonen["sjablonen"]:
                            print(f"    {Register().sjablonen[sjabloon_uuid]}")
                        
                        if invoer_kiezen(
                            beschrijving = "nog een sjabloon toevoegen?",
                            keuzes = {"ja": False, "nee": True},
                            kies_een = False,
                            ):
                            
                            break
                    
                    setgroep_type = invoer_kiezen(
                        beschrijving = "setgroep",
                        keuzes = {enum.value: enum for enum in SetGroepType},
                        )
                    
                    sjabloon_uuid = Register().sjablonen.filter(
                        weken = [0, cls.weken],
                        setgroep_type = setgroep_type,
                        gewicht_type = oefening_type.value[2],
                        ).kiezen()
                    sjabloon = Register().sjablonen[sjabloon_uuid]
                    
                    oefening_sjablonen["sjablonen"].append(sjabloon_uuid)
                    
                    if sjabloon.gewicht_type == GewichtType.PERCENTAGE:
                        
                        if not any([oefening == trainingsgewicht["oefening"] for trainingsgewicht in trainingsgewichten]):
                        
                            print(f"\ntrainingsgewicht nodig voor oefening \"{oefening.value[0]}\"")
                            
                            trainingsgewicht = invoer_validatie(
                                f"trainingsgewicht",
                                type = float,
                                )
                            
                            trainingsgewichten.append({
                                "oefening": oefening,
                                "trainingsgewicht": trainingsgewicht,
                                })
                
                oefeningen[f"dag {dag}"].append(oefening_sjablonen)
        
        cls.oefeningen = oefeningen
        cls.trainingsgewichten = trainingsgewichten
        cls.sessies = sessies
        
        if len(Register().schema.filter(status = Status.HUIDIG)) == 0:
            cls.status = Status.HUIDIG
        
        return cls

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