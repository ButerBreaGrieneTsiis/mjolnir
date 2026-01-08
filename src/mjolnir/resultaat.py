from dataclasses import dataclass
import datetime as dt
from pathlib import Path
import re
from typing import Any, ClassVar, Dict, List, TYPE_CHECKING

from grienetsiis import Decoder, opslaan_json, openen_json

from mjolnir.enums import OefeningEnum, GewichtType, ENUMS


if TYPE_CHECKING:
    from mjolnir.sessie import Sessie, SessieOefening, SessieSet

@dataclass
class ResultaatSet:
    
    repetities: int
    gewicht: float | None = None
    
    DECODER: ClassVar[Decoder | None] = None
    
    @classmethod
    def van_sessie(
        cls,
        sessie_set: "SessieSet",
        ) -> "ResultaatSet":
        
        if sessie_set.gewicht_type == GewichtType.GEWICHTLOOS:
            return cls(
                repetities = sessie_set.repetitie_gedaan,
                )
        return cls(
            repetities = sessie_set.repetitie_gedaan,
            gewicht = sessie_set.gewicht_gedaan,
            )
    
    @classmethod
    def van_json(
        cls,
        **dict,
        ) -> "ResultaatOefening":
        
        return cls(**dict)
    
    def naar_json(self) -> Dict[str, Any]:
        if self.gewicht is None:
            return {
                "repetities": self.repetities,
                }
        return {
                "repetities": self.repetities,
                "gewicht": self.gewicht,
                }
    
    @property
    def volume(self) -> float | None:
        if self.gewicht is None:
            return None
        return self.gewicht * self.repetities
    
    @property
    def e1rm(self) -> float | None:
        if self.gewicht is None:
            return None
        return round(self.gewicht * (1 + self.repetities/30), 2)

@dataclass
class ResultaatOefening:
    
    oefening: OefeningEnum
    sets: List[ResultaatSet]
    
    DECODER: ClassVar[Decoder | None] = None
    
    @classmethod
    def van_sessie(
        cls,
        sessie_oefening: "SessieOefening",
        ) -> "ResultaatOefening":
        
        sets = []
        
        for sessie_setgroep in sessie_oefening.sets.values():
            for sessie_set in sessie_setgroep:
                resultaat_set = ResultaatSet.van_sessie(sessie_set)
                sets.append(resultaat_set)
        
        return cls(
            oefening = sessie_oefening.oefening,
            sets = sets,
            )
    
    @classmethod
    def van_json(
        cls,
        **dict,
        ) -> "ResultaatOefening":
        
        return cls(**dict)
    
    def naar_json(self) -> Dict[str, Any]:
        return {
            "oefening": self.oefening,
            "sets": self.sets,
            }
    
    @property
    def volume(self) -> float | None:
        som = sum(set.volume for set in self.sets if set.volume is not None)
        return som if som > 0.0 else None
    
    @property
    def e1rm(self) -> float | None:
        e1rm = max(set.e1rm for set in self.sets if set.e1rm is not None)
        return e1rm if e1rm > 0.0 else None
    
    @staticmethod
    def recent(
        oefening: OefeningEnum,
        aantal: int = 10,
        ) -> Dict[str, List[str]]:
        
        resultaten = []
        
        gegevenspad = Path(f"gegevens\\sessies")
        bestandspaden = [bestand for bestand in gegevenspad.iterdir() if re.search(r"^gegevens\\sessies\\\d{4}-\d{2}-\d{2}.json$", str(bestand))]
        
        for bestandspad in reversed(bestandspaden):
            resultaat = Resultaat.openen(bestandspad)
            
            for resultaat_oefening in resultaat.oefeningen:
                if resultaat_oefening.oefening == oefening:
                    resultaten.append({
                        "datum": resultaat.datum,
                        "resultaat": resultaat_oefening,
                        })
                    break
            
            if len(resultaten) == aantal:
                break
        
        if len(resultaten) == 0:
            return {}
        
        resultaten_dict = {
            "datum": [],
            "volume": [],
            "e1rm": [],
            } | {
            f"set_{nummer + 1}": [] for nummer in range(max(len(resultaat["resultaat"].sets) for resultaat in resultaten))
            }
        
        for resultaat in resultaten:
            resultaten_dict["datum"].append(resultaat["datum"].strftime("%a %d %b %Y"))
            resultaten_dict["volume"].append(resultaat["resultaat"].volume)
            resultaten_dict["e1rm"].append(resultaat["resultaat"].e1rm)
            
            for nummer, resultaat_set in enumerate(resultaat["resultaat"].sets):
                resultaten_dict[f"set_{nummer + 1}"].append(resultaat_set.__repr__())
        
        return resultaten_dict
    
    @staticmethod
    def recent_e1rm(
        oefening: OefeningEnum,
        aantal: int = 10,
        ) -> List[Dict[str, Any]]:
        
        resultaten = ResultaatOefening.recent(
            oefening = oefening,
            aantal = aantal,
            )
        e1rms = []
        
        for resultaat in resultaten:
            
            e1rm = max(resultaat_set.e1rm for resultaat_set in resultaat["resultaat"].sets)
            e1rms.append({
                "datum": resultaat["datum"],
                "e1rm": e1rm,
                })
        
        return e1rms

@dataclass
class Resultaat:
    
    schema_uuid: str
    week: int
    dag: int
    datum: dt.date
    oefeningen: List[ResultaatOefening]
    
    DECODER: ClassVar[Decoder | None] = None
    
    @classmethod
    def van_sessie(
        cls,
        sessie: "Sessie",
        ) -> "Resultaat":
        
        oefeningen = []
        
        for sessie_oefening in sessie.oefeningen:
            
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
                decoder_lijst = [
                    Resultaat.DECODER,
                    ResultaatOefening.DECODER,
                    ResultaatSet.DECODER,
                    ],
                enum_dict = ENUMS,
                )
    
    def opslaan(self):
        opslaan_json(
            object = self,
            bestandspad = self.bestandspad,
            encoder_dict = {
                "Resultaat": "naar_json",
                "ResultaatOefening": "naar_json",
                "ResultaatSet": "naar_json",
                },
            enum_dict = ENUMS,
            )
    
    def naar_json(self) -> Dict[str, Any]:
        return {
            "schema_uuid": self.schema_uuid,
            "week": self.week,
            "dag": self.dag,
            "datum": self.datum.strftime("%Y-%m-%d"),
            "oefeningen": self.oefeningen,
            }
    
    @property
    def bestandspad(self) -> Path:
        return Path(f"gegevens\\sessies\\{self.datum.strftime("%Y-%m-%d")}.json")

ResultaatSet.DECODER = Decoder(
    decoder_functie = ResultaatSet.van_json,
    velden = frozenset((
        "repetities",
        "gewicht",
        ))
    )
ResultaatOefening.DECODER = Decoder(
    decoder_functie = ResultaatOefening.van_json,
    velden = frozenset((
        "oefening",
        "sets",
        ))
    )
Resultaat.DECODER = Decoder(
    decoder_functie = Resultaat.van_json,
    velden = frozenset((
        "schema_uuid",
        "week",
        "dag",
        "datum",
        "oefeningen",
        ))
    )