from dataclasses import dataclass
import datetime as dt
from pathlib import Path
from typing import Any, Dict, List

from grienetsiis import opslaan_json, openen_json

from mjolnir.enums import GewichtType, ENUMS


@dataclass
class Resultaat:
    
    schema_uuid: str
    week: int
    dag: int
    datum: dt.date
    resultaten: List[Dict[str, Any]]
    
    @classmethod
    def van_sessie(
        cls,
        sessie
        ) -> "Resultaat":
        
        resultaten = []
        
        for oefening in sessie.oefeningen:
            
            oefening_dict = {
                "oefening": oefening.oefening,
                "sets": [],
                }
            
            for sets in oefening.sets.values():
                for set in sets:
                    if set.gewicht_type == GewichtType.GEWICHTLOOS:
                        oefening_dict["sets"].append({
                            "repetities": set.repetitie_gedaan,
                            })
                    else:
                        oefening_dict["sets"].append({
                            "repetities": set.repetitie_gedaan,
                            "gewicht": set.gewicht_gedaan,
                            })
            
            resultaten.append(oefening_dict)
        
        return cls(
            schema_uuid = sessie.schema_uuid,
            week = sessie.week,
            dag = sessie.dag,
            datum = sessie.datum,
            resultaten = resultaten,
            )
    
    @classmethod
    def van_json(
        cls,
        **dict,
        ) -> "Resultaat":
        
        if "datum" in dict:
            dict["datum"] = dt.datetime.strptime(dict["datum"], "%Y-%m-%d").date()
        
        return cls(**dict)
    
    @classmethod
    def openen(
        cls,
        datum: dt.date,
        ) -> "Resultaat":
        
        bestandspad = Path(f"gegevens\\sessies\\{datum.strftime("%Y-%m-%d")}.json")
        
        if bestandspad.is_file():
            
            return openen_json(
                bestandspad = bestandspad,
                decoder_functie = cls.van_json,
                enum_dict = ENUMS,
                )
    
    def opslaan(self):
        
        bestandspad = Path(f"gegevens\\sessies\\{self.datum.strftime("%Y-%m-%d")}.json")
        
        sessie = {
            "schema_uuid": self.schema_uuid,
            "week": self.week,
            "dag": self.dag,
            "datum": self.datum.strftime("%Y-%m-%d"),
            "resultaten": self.resultaten,
            }
        
        opslaan_json(
            sessie,
            bestandspad,
            enum_dict = ENUMS,
            )