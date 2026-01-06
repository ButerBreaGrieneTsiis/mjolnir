from dataclasses import dataclass
import datetime as dt
from pathlib import Path
import re
from typing import Any, Dict, List

from grienetsiis import opslaan_json, openen_json

from mjolnir.enums import OefeningEnum, GewichtType, ENUMS


@dataclass
class Resultaat:
    
    schema_uuid: str
    week: int
    dag: int
    datum: dt.date
    oefeningen: List[Dict[str, Any]]
    
    @classmethod
    def van_sessie(
        cls,
        sessie
        ) -> "Resultaat":
        
        oefeningen = []
        
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
            
            oefeningen.append(oefening_dict)
        
        return cls(
            schema_uuid = sessie.schema_uuid,
            week = sessie.week,
            dag = sessie.dag,
            datum = sessie.datum,
            oefeningen = oefeningen,
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
        bestandspad: Path,
        ) -> "Resultaat":
            return openen_json(
                bestandspad = bestandspad,
                decoder_functie = cls.van_json,
                enum_dict = ENUMS,
                )
    
    def opslaan(self):
        
        opslaan_json(
            self.naar_json(),
            self.bestandspad,
            enum_dict = ENUMS,
            )
    
    def naar_json(self):
        return {
            "schema_uuid": self.schema_uuid,
            "week": self.week,
            "dag": self.dag,
            "datum": self.datum.strftime("%Y-%m-%d"),
            "oefeningen": self.oefeningen,
            }
    
    @staticmethod
    def oefening(
        oefening: OefeningEnum,
        aantal: int = 10,
        ) -> List[Dict[str, Any]]:
        
        resultaten = []
        
        gegevenspad = Path(f"gegevens\\sessies")
        bestandspaden = [bestand for bestand in gegevenspad.iterdir() if re.search(r"^gegevens\\sessies\\\d{4}-\d{2}-\d{2}.json$", str(bestand))]
        
        for bestandspad in reversed(bestandspaden):
            resultaat = Resultaat.openen(bestandspad)
            
            for _oefening in resultaat.oefeningen:
                if _oefening["oefening"] == oefening:
                    resultaten.append({
                        "datum": resultaat.datum,
                        "sets": _oefening["sets"],
                        })
                    
                    break
            
            if len(resultaten) == aantal:
                break
        
        return resultaten
    
    @staticmethod
    def e1rm(
        oefening: OefeningEnum,
        aantal: int = 10,
        ) -> List[Dict[str, Any]]:
        
        resultaten = Resultaat.oefening(oefening, aantal)
        e1rms = []
        
        for resultaat in resultaten:
            
            e1rm = max(Resultaat.epley(set["gewicht"], set["repetities"]) for set in resultaat["sets"])
            e1rms.append({
                "datum": resultaat["datum"],
                "e1rm": e1rm,
                })
        
        return e1rms
    
    @staticmethod
    def epley(
        gewicht: float,
        repetities: int,
        ) -> float:
        return gewicht * (1 + repetities/30)
    
    @property
    def bestandspad(self) -> Path:
        return Path(f"gegevens\\sessies\\{self.datum.strftime("%Y-%m-%d")}.json")