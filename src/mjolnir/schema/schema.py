from dataclasses import dataclass
import datetime as dt
from typing import ClassVar, Dict, List

from mjolnir.kern import CONFIG, Register, GeregistreerdObject
from mjolnir.kern.enums import OefeningType, GewichtType, Oefening, Status, SetGroepType
from mjolnir.schema.sjabloon import Sjabloon

from grienetsiis.opdrachtprompt import invoeren, kiezen


@dataclass
class Schema(GeregistreerdObject):
    
    naam: str
    weken: int
    dagen: int
    status: Status = Status.GEPLAND
    datum_begin: dt.date | None = None
    datum_eind: dt.date | None = None
    oefeningen: Dict[str, Dict[str, List[Sjabloon]]] | None = None
    trainingsgewichten: List[Dict[str, Oefening | float]] | None = None
    sessies: Dict[str, Dict[str, dt.date]] | None = None
    
    BESTANDSNAAM: ClassVar[str] = "schema"
    
    def __repr__(self) -> str:
        return f"{self.naam} ({self.status.value})"
    
    @classmethod
    def nieuw(
        cls,
        velden,
        ) -> "Schema":
        
        schema = super().nieuw(velden)
        
        oefeningen = {}
        trainingsgewichten = []
        sessies = {}
        
        for week in range(1, schema.weken + 1):
            sessies[f"week {week}"] = {}
            for dag in range(1, schema.dagen + 1):
                sessies[f"week {week}"][f"dag {dag}"] = {
                    "datum": None,
                    "status": Status.GEPLAND,
                    }
        
        for dag in range(1, schema.dagen + 1):
            
            oefeningen[f"dag {dag}"] = []
            
            print(f"\ntoevoegen oefeningen voor dag {dag}")
            
            while True:
                
                if len(oefeningen[f"dag {dag}"]) > 0:
                    print(f"\nschema voor dag {dag}")
                    for oefening_sjablonen in oefeningen[f"dag {dag}"]:
                        print(f"  oefening \"{oefening_sjablonen["oefening"].naam}\"")
                        for sjabloon_uuid in oefening_sjablonen["sjablonen"]:
                            print(f"    {Register().sjablonen[sjabloon_uuid]}")
                    
                    if kiezen(
                        beschrijving = "nog een oefening toevoegen?",
                        keuzes = {"ja": False, "nee": True},
                        kies_een = False,
                        ):
                        
                        break
                
                oefening_type = kiezen(
                    beschrijving = "oefeningstype",
                    keuzes = {oefening_type.naam: oefening_type for oefening_type in OefeningType},
                    )
                
                oefening = kiezen(
                    beschrijving = "oefening",
                    keuzes = {oefening.naam: oefening for oefening in Oefening if oefening.oefening_type == oefening_type},
                    )
                
                print(f"\n>>> oefening \"{oefening.naam}\" gekozen")
                
                oefening_sjablonen = {
                    "oefening": oefening,
                    "sjablonen": [],
                    }
                
                while True:
                    
                    if len(oefening_sjablonen["sjablonen"]) > 0:
                        print(f"\nsjablonen voor {oefening.naam}")
                        for sjabloon_uuid in oefening_sjablonen["sjablonen"]:
                            print(f"    {Register().sjablonen[sjabloon_uuid]}")
                        
                        if kiezen(
                            beschrijving = "nog een sjabloon toevoegen?",
                            keuzes = {"ja": False, "nee": True},
                            kies_een = False,
                            ):
                            
                            break
                    
                    setgroep_type = kiezen(
                        beschrijving = "setgroep",
                        keuzes = {setgroep_type.value: setgroep_type for setgroep_type in SetGroepType},
                        )
                    
                    sjabloon_uuid = Register().sjablonen.filter(
                        weken = [0, schema.weken],
                        setgroep_type = setgroep_type,
                        gewicht_type = oefening_type.gewicht_types,
                        ).kiezen()
                    sjabloon = Register().sjablonen[sjabloon_uuid]
                    
                    oefening_sjablonen["sjablonen"].append(sjabloon_uuid)
                    
                    if sjabloon.gewicht_type == GewichtType.PERCENTAGE:
                        
                        if not any([oefening == trainingsgewicht["oefening"] for trainingsgewicht in trainingsgewichten]):
                        
                            print(f"\ntrainingsgewicht nodig voor oefening \"{oefening.naam}\"")
                            
                            trainingsgewicht = invoeren(
                                beschrijving = "trainingsgewicht",
                                type = float,
                                bereik = (0.0, CONFIG["GEWICHT_AANTAL_MAX"]),
                                )
                            
                            trainingsgewichten.append({
                                "oefening": oefening,
                                "trainingsgewicht": trainingsgewicht,
                                })
                
                oefeningen[f"dag {dag}"].append(oefening_sjablonen)
        
        schema.oefeningen = oefeningen
        schema.trainingsgewichten = trainingsgewichten
        schema.sessies = sessies
        
        if len(Register().schema.filter(status = Status.HUIDIG)) == 0:
            schema.status = Status.HUIDIG
        
        return schema