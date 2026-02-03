"""mjolnir.resultaat.resultaat"""
from __future__ import annotations
from dataclasses import dataclass
import datetime as dt
from pathlib import Path
import re
from typing import Any, Callable, ClassVar, Dict, List, TYPE_CHECKING

from grienetsiis.gereedschap import formatteer_getal
from grienetsiis.json import opslaan_json, openen_json
from grienetsiis.register import Register

from mjolnir.kern.enums import Oefening, Status, ENUMS
from mjolnir.resultaat import ResultaatSet, ResultaatOefening

if TYPE_CHECKING:
    from mjolnir.sessie.sessie import Sessie


@dataclass
class Resultaat:
    
    schema_uuid: str
    week: int
    dag: int
    datum: dt.date
    oefeningen: List[ResultaatOefening]
    
    ONTCIJFERAAR_FUNCTIE: ClassVar[Callable | None] = None
    VERCIJFERAAR_FUNCTIE: ClassVar[Callable | None] = None
    
    # CLASS METHODS
    
    @classmethod
    def van_sessie(
        cls,
        sessie: Sessie,
        ) -> Resultaat:
        
        oefeningen = []
        
        for sessie_oefening in sessie.oefeningen:
            if any(sessie_set.status == Status.AFGEROND and sessie_set.repetitie_gedaan > 0 for sessie_setgroep in sessie_oefening.sets.values() for sessie_set in sessie_setgroep):
                resultaat_oefening = ResultaatOefening.van_sessie(sessie_oefening)
                oefeningen.append(resultaat_oefening)
        
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
        ) -> Resultaat:
        
        return cls(**dict)
    
    @classmethod
    def openen(
        cls,
        bestandspad: Path,
        ) -> Resultaat:
            
            return openen_json(
                bestandspad = bestandspad,
                ontcijfer_functie_object = Resultaat.ONTCIJFERAAR_FUNCTIE,
                ontcijfer_functie_subobjecten = [
                    ResultaatOefening.ONTCIJFERAAR,
                    ResultaatSet.ONTCIJFERAAR,
                    ],
                ontcijfer_enum = ENUMS,
                )
    
    # INSTANCE METHODS
    
    def opslaan(self):
        
        opslaan_json(
            object = self,
            bestandspad = self.bestandspad,
            vercijfer_functie_object = Resultaat.VERCIJFERAAR_FUNCTIE,
            vercijfer_functie_subobjecten = [
                ResultaatOefening.VERCIJFERAAR,
                ResultaatSet.VERCIJFERAAR,
                ],
            vercijfer_enum = ENUMS,
            )
    
    def naar_json(self) -> Dict[str, Any]:
        
        return {
            "schema_uuid": self.schema_uuid,
            "week": self.week,
            "dag": self.dag,
            "datum": self.datum,
            "oefeningen": self.oefeningen,
            }
    
    # STATIC METHODS
    
    @staticmethod
    def tabel_recent(
        oefening: Oefening,
        aantal: int = 10,
        ) -> Dict[str, List[Any]]:
        
        resultaten = []
        
        gegevenspad = Path(f"gegevens\\sessies")
        bestandspaden = [bestand for bestand in gegevenspad.iterdir() if re.search(r"^gegevens\\sessies\\\d{4}-\d{2}-\d{2}.json$", str(bestand))]
        
        for bestandspad in reversed(bestandspaden):
            resultaat = Resultaat.openen(bestandspad)
            
            for resultaat_oefening in resultaat.oefeningen:
                if resultaat_oefening.oefening == oefening:
                    resultaten.append({
                        "datum": resultaat.datum,
                        "schema": Register().schema[resultaat.schema_uuid].naam,
                        "week": resultaat.week,
                        "dag": resultaat.dag,
                        "resultaat_oefening": resultaat_oefening,
                        })
                    break
            
            if len(resultaten) == aantal:
                break
        
        if len(resultaten) == 0:
            return {}
        
        resultaten_dict = {
            "datum": [],
            "schema": [],
            "week": [],
            "dag": [],
            "#sets": [],
            "sets": [],
            }
        
        if oefening.dextraal:
            resultaten_dict["sets (r)"] = []
            resultaten_dict["sets (l)"] = []
        
        if not oefening.gewichtloos:
            resultaten_dict["volume"] = []
            resultaten_dict["e1rm"] = []
            if oefening.dextraal:
                resultaten_dict["volume (r)"] = []
                resultaten_dict["volume (l)"] = []
                resultaten_dict["e1rm (r)"] = []
                resultaten_dict["e1rm (l)"] = []
        
        for resultaat in resultaten:
            resultaten_dict["datum"].append(resultaat["datum"].strftime("%a %d %b %Y"))
            resultaten_dict["#sets"].append(len(resultaat["resultaat_oefening"].sets))
            resultaten_dict["sets"].append(resultaat["resultaat_oefening"].tekst)
            if oefening.dextraal:
                resultaten_dict["sets (r)"].append(resultaat["resultaat_oefening"].tekst)
                resultaten_dict["sets (l)"].append(resultaat["resultaat_oefening"].tekst_links)
            if not oefening.gewichtloos:
                resultaten_dict["volume"].append(formatteer_getal(resultaat["resultaat_oefening"].volume))
                resultaten_dict["e1rm"].append(formatteer_getal(resultaat["resultaat_oefening"].e1rm))
                if oefening.dextraal:
                    resultaten_dict["volume (r)"].append(formatteer_getal(resultaat["resultaat_oefening"].volume))
                    resultaten_dict["volume (l)"].append(formatteer_getal(resultaat["resultaat_oefening"].volume_links))
                    resultaten_dict["e1rm (r)"].append(formatteer_getal(resultaat["resultaat_oefening"].e1rm))
                    resultaten_dict["e1rm (l)"].append(formatteer_getal(resultaat["resultaat_oefening"].e1rm_links))
            resultaten_dict["schema"].append(resultaat["schema"])
            resultaten_dict["week"].append(resultaat["week"])
            resultaten_dict["dag"].append(resultaat["dag"])
        
        if oefening.dextraal:
            resultaten_dict.pop("sets")
            resultaten_dict.pop("volume")
            resultaten_dict.pop("e1rm")
        
        return resultaten_dict
    
    # PROPERTIES
    
    @property
    def bestandspad(self) -> Path:
        return Path(f"gegevens\\sessies\\{self.datum.strftime("%Y-%m-%d")}.json")



Resultaat.ONTCIJFERAAR_FUNCTIE = Resultaat.van_json
Resultaat.VERCIJFERAAR_FUNCTIE = Resultaat.naar_json