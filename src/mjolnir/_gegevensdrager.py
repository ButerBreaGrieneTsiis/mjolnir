import datetime as dt
from pathlib import Path
from typing import Any, Callable, Dict, List

from grienetsiis import openen_json, opslaan_json, Decoder

from .enums import ENUM_DICT
from ._register import _Register


class BasisType:
    
    BESTANDSMAP: Path = Path("gegevens")
    EXTENSIE: str = "json"
    
    @classmethod
    def van_json(
        cls,
        **dict,
        ) -> "BasisType":
        
        if "datum" in dict:
            dict["datum"] = dt.datetime.strptime(dict["datum"], "%Y-%m-%d").date()
        
        return cls(**dict)
    
    def naar_json(self) -> Dict[str, Any]:
        
        dict_naar_json = {}
        
        for sleutel, waarde in self.__dict__.items():
            
            # alle velden uitsluiten die standaardwaardes hebben; nutteloos om op te slaan
            if waarde is None:
                continue
            elif isinstance(waarde, bool) and not waarde:
                continue
            elif isinstance(waarde, list) and len(waarde) == 0:
                continue
            elif isinstance(waarde, dict) and not bool(waarde):
                continue
            elif isinstance(waarde, str) and waarde == "":
                continue
            elif isinstance(waarde, int) and waarde == 0:
                continue
            elif sleutel == "uuid":
                continue
            
            # overige velden deserialiseren
            elif isinstance(waarde, dt.date):
                dict_naar_json[sleutel] = waarde.strftime("%Y-%m-%d")
            
            # alle overige velden toevoegen
            else:
                dict_naar_json[sleutel] = waarde
        
        return dict_naar_json

class Databank:
    
    BESTANDSMAP: Path = Path("gegevens")
    EXTENSIE: str = "json"
    
    DECODER_FUNCTIE: Callable = None
    DECODER_LIJST: List[Decoder] = None
    
    ENCODER_FUNCTIE: Callable = None
    ENCODER_DICT: Dict[str, str] = None
    
    @classmethod
    def openen(cls) -> "Databank":
        
        if not cls.BESTANDSMAP.is_dir():
            cls.BESTANDSMAP.mkdir()
        
        bestandspad = cls.BESTANDSMAP / f"{cls.BESTANDSNAAM}.{cls.EXTENSIE}"
        
        if bestandspad.is_file():
            
            return cls(openen_json(
                bestandspad,
                decoder_functie = cls.DECODER_FUNCTIE,
                decoder_lijst = cls.DECODER_LIJST,
                enum_dict = ENUM_DICT,
                ))
        else:
            return cls()
    
    def opslaan(self) -> None:
        bestandspad = self.BESTANDSMAP / f"{self.BESTANDSNAAM}.{self.EXTENSIE}"
        
        opslaan_json(
            self,
            bestandspad,
            encoder_functie = self.ENCODER_FUNCTIE,
            encoder_dict = self.ENCODER_DICT,
            enum_dict = ENUM_DICT,
            )

class DatabankDict(Databank, dict):
    
    @property
    def lijst(self) -> List[BasisType]:
        return list(self.values())

class DatabankLijst(Databank, list):
    
    pass
