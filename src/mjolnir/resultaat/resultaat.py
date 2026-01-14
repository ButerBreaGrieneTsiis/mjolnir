from dataclasses import dataclass
import datetime as dt
from pathlib import Path
import re
from typing import Any, Callable, ClassVar, Dict, List, TYPE_CHECKING

from grienetsiis import Decoder, Encoder, opslaan_json, openen_json, decimaal_getal

from mjolnir.basis import Register
from mjolnir.basis.enums import Oefening, GewichtType, Status, ENUMS


if TYPE_CHECKING:
    from mjolnir.sessie.sessie import Sessie, SessieOefening, SessieSet

@dataclass
class ResultaatSet:
    
    repetities: int
    gewicht: float | None = None
    
    DECODER: ClassVar[Decoder | None] = None
    ENCODER: ClassVar[Encoder | None] = None
    
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
    def tekst(self) -> str:
        if self.gewicht is None:
            return f"{self.repetities}"
        
        gewicht_tekst = f"{self.gewicht:.2f}"
        if gewicht_tekst[-2:] == "00":
            return f"{self.repetities}@{gewicht_tekst[:-3]}"
        if gewicht_tekst[-1] == "0":
            return f"{self.repetities}@{gewicht_tekst[:-1]}"
        return f"{self.repetities}@{gewicht_tekst}"
    
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
    
    oefening: Oefening
    sets: List[ResultaatSet]
    
    DECODER: ClassVar[Decoder | None] = None
    ENCODER: ClassVar[Encoder | None] = None
    
    @classmethod
    def van_sessie(
        cls,
        sessie_oefening: "SessieOefening",
        ) -> "ResultaatOefening":
        
        sets = []
        
        for sessie_setgroep in sessie_oefening.sets.values():
            for sessie_set in sessie_setgroep:
                if sessie_set.status == Status.AFGEROND and sessie_set.repetitie_gedaan > 0:
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
    def tekst(self) -> str:
        
        if len(set(resultaat_set.gewicht for resultaat_set in self.sets)) == 1 and len(set(resultaat_set.repetities for resultaat_set in self.sets)):
            if self.sets[0].gewicht is not None:
                return f"{len(self.sets)}x{self.sets[0].repetities}@{self.sets[0].gewicht}"
            return f"{len(self.sets)}x{self.sets[0].repetities}"
        
        if len(set(resultaat_set.gewicht for resultaat_set in self.sets)):
            if self.sets[0].gewicht is not None:
                return "(" + ", ".join(f"{resultaat_set.repetities}" for resultaat_set in self.sets) + f")@{self.sets[0].gewicht}"
            return  ", ".join(f"{resultaat_set.repetities}" for resultaat_set in self.sets)
        
        if len(set(resultaat_set.repetities for resultaat_set in self.sets)):
            return f"{len(self.sets)}x{self.sets[0].repetities}@(" + ", ".join(f"{resultaat_set.gewicht}" for resultaat_set in self.sets) + ")"
        
        return ", ".join(resultaat_set.tekst for resultaat_set in self.sets)
    
    @property
    def volume(self) -> float | None:
        if self.oefening.gewichtloos:
            return None
        return sum(set.volume for set in self.sets)
    
    @property
    def e1rm(self) -> float | None:
        if self.oefening.gewichtloos:
            return None
        return max(set.e1rm for set in self.sets)
    
    @staticmethod
    def recent(
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
            "#sets": [],
            "sets": [],
            "schema": [],
            "week": [],
            "dag": [],
            }
        
        if not oefening.gewichtloos:
            resultaten_dict["volume"] = []
            resultaten_dict["e1rm"] = []
        
        for resultaat in resultaten:
            resultaten_dict["datum"].append(resultaat["datum"].strftime("%a %d %b %Y"))
            resultaten_dict["#sets"].append(len(resultaat["resultaat_oefening"].sets))
            resultaten_dict["sets"].append(resultaat["resultaat_oefening"].tekst)
            if not oefening.gewichtloos:
                resultaten_dict["volume"].append(decimaal_getal(resultaat["resultaat_oefening"].volume))
                resultaten_dict["e1rm"].append(decimaal_getal(resultaat["resultaat_oefening"].e1rm))
            resultaten_dict["schema"].append(resultaat["schema"])
            resultaten_dict["week"].append(resultaat["week"])
            resultaten_dict["dag"].append(resultaat["dag"])
        
        return resultaten_dict

@dataclass
class Resultaat:
    
    schema_uuid: str
    week: int
    dag: int
    datum: dt.date
    oefeningen: List[ResultaatOefening]
    
    DECODER_FUNCTIE: ClassVar[Callable | None] = None
    ENCODER_FUNCTIE: ClassVar[Callable | None] = None
    
    @classmethod
    def van_sessie(
        cls,
        sessie: "Sessie",
        ) -> "Resultaat":
        
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
        ) -> "Resultaat":
        
        return cls(**dict)
    
    @classmethod
    def openen(
        cls,
        bestandspad: Path,
        ) -> "Resultaat":
            
            return openen_json(
                bestandspad = bestandspad,
                decoder_object = Resultaat.DECODER_FUNCTIE,
                decoder_subobjecten = [
                    ResultaatOefening.DECODER,
                    ResultaatSet.DECODER,
                    ],
                enum_dict = ENUMS,
                )
    
    def opslaan(self):
        
        opslaan_json(
            object = self,
            bestandspad = self.bestandspad,
            encoder_object = Resultaat.ENCODER_FUNCTIE,
            encoder_subobjecten = [
                ResultaatOefening.ENCODER,
                ResultaatSet.ENCODER,
                ],
            enum_dict = ENUMS,
            )
    
    def naar_json(self) -> Dict[str, Any]:
        
        return {
            "schema_uuid": self.schema_uuid,
            "week": self.week,
            "dag": self.dag,
            "datum": self.datum,
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
ResultaatSet.ENCODER = Encoder(
    class_naam = "ResultaatSet",
    encoder_functie = "naar_json",
    )
ResultaatOefening.DECODER = Decoder(
    decoder_functie = ResultaatOefening.van_json,
    velden = frozenset((
        "oefening",
        "sets",
        ))
    )
ResultaatOefening.ENCODER = Encoder(
    class_naam = "ResultaatOefening",
    encoder_functie = "naar_json",
    )
Resultaat.DECODER_FUNCTIE = Resultaat.van_json
Resultaat.ENCODER_FUNCTIE = Resultaat.naar_json